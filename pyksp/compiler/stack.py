from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal
from native_types import KspNative

from local_types import KspLocal

# from interfaces import IOutput

from abstract import KSP
from dev_tools import expand_if_callable

from loops import For


class StackFrame:

    def __init__(self, *vars):
        self.items = dict()
        self.size = 0
        for var in vars:
            self.items[var.name] = var
            self.size += var.len

    def __getitem__(self, key):
        return self.items[key]


class FrameVar:

    def __init__(self, name: str, val: object,
                 start_idx: int, length: int):
        self.val = val
        self.name = name
        if length:
            self.len = length
            return
        try:
            self.len = len(val)
        except TypeError:
            self.len = 1


class FrameVarLocal(FrameVar):

    def __init__(self, name: str, seq: KspNative,
                 start_idx: int, length: int):
        self.val = seq
        self.name = name
        self.start_idx = start_idx
        self.len = length

    def __call__(self, value=None):
        if not value:
            return (self.val[self.start_idx])
        if self.len == 1:
            self.val[self.start_idx] = value
            return
        raise TypeError("can't be called")

    def __getitem__(self, idx):
        if self.len == 1:
            raise TypeError("is not sequence")
        self.__check_idx(idx)
        idx = expand_if_callable(self.start_idx + idx)
        return self.val[idx]

    def __setitem__(self, idx, value):
        if self.len == 1:
            raise TypeError("is not sequence")
        self.__check_idx(idx)
        idx = expand_if_callable(self.start_idx + idx)
        self.val[idx] = value

    def __check_idx(self, idx):
        if idx > self.len - 1:
            raise IndexError(f'idx [{idx}] is out of range')


class Stack(KSP):
    '''Basic stack implementation in pure KSP.
    Handles only one datatype per stack object.
    Useful for making functions and recursion implementation'''

    def __init__(self, name: str, size: int,
                 ref_type: KspNative, recursion_depth: int=100):
        self.ref_type = ref_type
        arr_type = self._get_arr_type(ref_type)

        self.idx_curr = kInt('stack_%s_curr' % name, 0)
        self.arr = arr_type('stack_%s_arr' % name, length=size)
        self.idx_arr = kArrInt('stack_%s_idx' % name,
                               length=recursion_depth)

        self.frames = list()

    def _get_arr_type(self, ref_type):
        if ref_type in (kInt, kArrInt, int):
            return kArrInt
        if ref_type in (kStr, kArrStr, str):
            return kArrStr
        if ref_type in (kReal, kArrReal, float):
            return kArrReal

    def push_arg(self, name, val, count):
        try:
            is_arr = len(val)
        except TypeError:
            is_arr = False
        idx = self.idx_arr[self.idx_curr]

        if not is_arr:
            # val = expand_if_callable(val)
            self.arr[idx + count] = val
            val = self.arr[idx + count]
            var = FrameVar(name, val, length=1)
            return var, count + 1

        with For(arr=val) as arr:
            for i, item in enumerate(arr):
                arr_idx = idx + count + i
                item = expand_if_callable(item)
                self.arr[arr_idx] = item
        val, length = self.__build_frame_arr(val, idx, count)

        var = FrameVar(name, val, length)
        return var, count + length

    def puch_local_arg(self, name, val, count):
        try:
            is_arr = len(val)
        except TypeError:
            is_arr = False
        idx = self.idx_arr[self.idx_curr]

        if not is_arr:
            var = FrameVarLocal(name, self.arr, idx + count, 1)
            return var, count + 1

        var = FrameVarLocal(name, self.arr, idx + count, is_arr)
        length = is_arr
        return var, count + length

    def __build_frame_arr(self, val, idx, count):
        new_val = list()
        for i, item in enumerate(val.value_get()):
            arr_idx = idx + count + i
            item = expand_if_callable(item)
            new_val.append(expand_if_callable(self.arr[arr_idx]))
        length = len(val)
        val = new_val
        return val, length

    def _build_frame(self, **kwargs):
        frame_vars = list()
        count = 0
        for key, val in kwargs.items():
            if isinstance(val, KspLocal):
                var, count = self.puch_local_arg(key, val, count)
            else:
                var, count = self.push_arg(key, val, count)
            frame_vars.append(var)
        self.frames.append(StackFrame(*frame_vars))

    def push(self, **kwargs):
        '''create StackFrame object from arguments
        and push it to stack.'''
        self._update_idx()
        self._build_frame(**kwargs)
        return

    def _update_idx(self):
        if not self.IsEmpty():
            frame = self.peek()
            self.idx_arr[self.idx_curr + 1] =\
                self.idx_arr[self.idx_curr] + frame.size
            self.idx_curr += 1

    def pop(self) -> StackFrame:
        '''get last frame and delete it'''
        self.idx_curr -= 1
        return self.frames.pop()

    def peek(self):
        '''get the last frame wihout deleting it'''
        return self.frames[-1]

    def IsEmpty(self):
        '''check stack for zero-length'''
        return len(self.frames) == 0
