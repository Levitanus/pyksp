# import collections

from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal
from native_types import KspNative
from native_types import KspNativeArray

# from local_types import KspLocal

# from interfaces import IOutput

from abstract import KSP
from dev_tools import expand_if_callable
from dev_tools import ref_type_from_input

from pyksp_ast import AstMethod
from pyksp_ast import AstAdd
# from pyksp_ast import AstAsgn

from loops import For


class StackArray(KspNativeArray):
    '''Used in stack as data array'''

    def __init__(self, name: str, ref_type: type, size: int):
        self.init_length = size
        if ref_type in (kArrInt, kInt, int):
            self.seq = kArrInt(name, length=size)
        if ref_type in (kArrStr, kStr, str):
            self.seq = kArrStr(name, length=size)
        if ref_type in (kArrReal, kReal, float):
            self.seq = kArrReal(name, length=size)
        self.ref_type = self.seq.ref_type
        self.name = self.seq.name

    def __call__(self):
        if not KSP.is_under_test():
            return self.seq.name()
        return self.seq()

    def __getitem__(self, idx):
        return self.seq[idx]

    def __setitem__(self, idx, val):
        self.seq[idx] = val

    def _generate_init(self):
        '''for blocking errors caused by inheritance'''
        pass


class kLocal:

    def __init__(self, ref_type: [int, str, float], length: int=1):
        self.len = length
        self.ref_type = ref_type


class FrameVar(KspNativeArray):

    def __init__(self, name, val, length=None,
                 start_idx=None):
        self._name = name
        self.name = self._name_func
        self.val = val
        if length:
            self.len = length
        else:
            try:
                self.len = len(val)
            except TypeError:
                self.len = 1
        self._start_idx = start_idx
        if start_idx is not None:
            assert isinstance(val, StackArray), \
                f'Expected {StackArray} or not start_idx'
            self.seq = self.val
        if self.len == 1:
            if start_idx is not None:
                self.ref_type = ref_type_from_input(self.val[0])
            else:
                self.ref_type = ref_type_from_input(self.val)
        else:
            self.ref_type = ref_type_from_input(self.val[0])
        self._iterated = False

    def value_get(self):
        if KSP.is_under_test():
            if self._start_idx is not None:
                if self.len == 1:
                    return self.val[self._start_idx]
                return [self.val[i]for i in
                        range(self._start_idx,
                              self._start_idx + self.len)]
            return self.val
        if self.len > 1:
            raise TypeError("can't return array on compilation")
        if self._start_idx is not None:
            return self.val[self._start_idx]
        return self.val

    def value_set(self, other):
        if not KSP.is_under_test():
            return
        if self.len == 1:
            if self._start_idx is not None:
                self.val[self._start_idx] = other
                return
            self.val.value_set(other)
            return
        raise TypeError('can not assign to array. use For()')

    def _name_func(self):
        '''intuition tells something wrong here'''
        if self._start_idx is not None:
            if self.len == 1:
                return f'{self.val.name()}[' +\
                    f'{expand_if_callable(self._start_idx)}]'
            return self.val.name()
        return self.val()

    def __call__(self, value=None):
        if value:
            assert self.len == 1, \
                "can't assign value to array. " +\
                "Use '<var>[idx] = val' instead"
            if self._start_idx is not None:
                self.val[self._start_idx] = value
                return
            self.val = value
            return
        if self.len > 1:
            assert not self._start_idx, \
                f"can't call {StackArray}. This ahoudn't has happend."
        if self._start_idx is not None:
            return self.val[self._start_idx]
        return expand_if_callable(self.val)

    def __getitem__(self, idx):
        if self.len == 1:
            raise TypeError("is not sequence")
        if self._start_idx:
            idx = self.__check_idx(idx)
            # idx = idx
        return self.val[idx]

    def __setitem__(self, idx, value):
        if self.len == 1:
            raise TypeError("is not sequence")
        if self._start_idx:
            idx = self.__check_idx(idx)
        self.val[idx] = value

    def __iter__(self):
        idx = self._start_idx
        length = self.len
        seq = self.val[idx:idx + length]
        return iter(seq)

    def __check_idx(self, idx):
        if not KSP.is_under_test() and isinstance(idx, KspNative):
            return self._start_idx + idx
        if idx >= self.len:
            raise IndexError(f'invalid index {idx}')
        if isinstance(idx, AstMethod):
            return AstAdd(self._start_idx, idx)
        return self._start_idx + idx

    def __len__(self):
        return self.len


class StackFrame:

    def __init__(self):
        self._vars = dict()
        self._keys = list()
        self.size = 0

    def __getitem__(self, key):
        return self._vars[key]

    def append(self, key: str, var: FrameVar):
        assert isinstance(var, FrameVar), \
            f'has to be {FrameVar}'
        assert key not in self._vars, \
            'var exists'
        assert isinstance(key, str), \
            'key has to be str'
        self._vars[key] = var
        self.size += var.len
        self._keys.append(key)

    def __iter__(self):
        for key in self._keys:
            yield self._vars[key]

    def items(self):
        return [var for var in self.__iter__()]

    def extend(self, **kwargs):
        for key, val in kwargs.items():
            self.append(key, val)


class Stack(KSP):
    '''Basic stack implementation in pure KSP.
    Handles only one datatype per stack object.
    Useful for making functions and recursion implementation'''

    def __init__(self, name: str, size: int,
                 ref_type: KspNative, recursion_depth: int=100):
        self.ref_type = ref_type

        self.idx_curr = kInt('stack_%s_curr' % name, 0)
        self.arr = StackArray('stack_%s_arr' % name, ref_type, size)
        self.idx_arr = kArrInt('stack_%s_idx' % name,
                               length=recursion_depth)

        self.frames = list()

    def _update_idx(self):
        if not self.IsEmpty():
            frame = self.peek()
            self.idx_arr[self.idx_curr + 1] =\
                self.idx_arr[self.idx_curr] + frame.size
            self.idx_curr += 1

    def _append_frame_item(self, name, item, frame, count):
        idx = self.idx_arr[self.idx_curr] + count
        if isinstance(item, kLocal):
            var = FrameVar(
                name,
                self.arr,
                length=item.len,
                start_idx=idx)
            frame.append(name, var)
            return count + item.len

        if KSP.is_under_test():
            var = FrameVar(name, item)
            frame.append(name, var)
            return count + var.len

        try:
            length = len(item)
            with For(arr=item, enumerate=True) as gen:
                for gen_idx, val in gen:
                    self.arr[idx + gen_idx] = val
            var = FrameVar(
                name,
                self.arr,
                length=length,
                start_idx=idx)
            frame.append(name, var)
            return count + length
        except TypeError:
            self.arr[idx] = item
            var = FrameVar(name, self.arr[idx], length=1)
            frame.append(name, var)
            return count + 1

    def push(self, **kwargs):
        self._update_idx()
        self.frames.append(StackFrame())
        frame = self.frames[-1]
        count = 0
        for name, item in kwargs.items():
            count = self._append_frame_item(name, item, frame, count)

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
