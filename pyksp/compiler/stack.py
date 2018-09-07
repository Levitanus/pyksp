from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal

from abstract import KSP
from base_types import KspArray
from base_types import KspVar
from base_types import KspIntVar
from base_types import KspRealVar
from base_types import KspStrVar

from conditions_loops import For


class kLoc(KSP):
    '''Special class for being argument annotation of functions
    or variable to put in stack.
    if size > 1 stack will return StackFrameArray object
    with size of 1 will return item of stack array

    Use it if You want to have true local variable inside a function
    '''

    def __init__(self,
                 ref_type: (int, str, float, kInt, kReal, kStr),
                 size: int=1):
        self.__size = size
        self.__type = self.__get_type(ref_type)

    def __get_type(self, ref_type):
        if ref_type in (int, kInt, KspIntVar):
            return kInt
        if ref_type in (str, kStr, KspStrVar):
            return kStr
        if ref_type in (float, kReal, KspRealVar):
            return kReal

    @property
    def _size(self):
        '''return size of kLoc'''
        return self.__size

    @property
    def ref_type(self):
        '''returns kInt, kStr or kReal depends on init'''
        return self.__type


class StackFrameArray(KspArray):
    '''wraps KspArray for being some sort of slice object
    has methods __getitem__ and __setitem__, using start_idx
    as shift and returns or assignes wrapped array item
    methods __len__ and iter_runtime are implemented
    methods append and extend are not
    '''

    def __init__(self, arr, start_idx, end_idx):
        self.__array = arr
        self.__start_idx = start_idx
        self.__length = self._get_runtime_idx(end_idx - start_idx)
        super().__init__(name=arr.name()[1:],
                         name_prefix=arr.name()[1],
                         name_postfix='',
                         preserve_name=False,
                         has_init=False,
                         is_local=True,
                         ref_type=arr.ref_type,
                         item_type=arr.item_type,
                         size=end_idx - start_idx,
                         seq=None,
                         persist=False,
                         def_val=None)

    def _get_compiled(self):
        raise NotImplementedError

    def _get_runtime(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        if self._get_runtime_idx(idx) >= \
                self._get_runtime_idx(self.__length):
            raise IndexError('index out of range')
        return self.__array[idx + self.__start_idx]

    def __setitem__(self, idx, val):
        if self._get_runtime_idx(idx) >= self.__len__():
            raise IndexError('index out of range')
        self.__array[idx + self.__start_idx] <<= val

    def iter_runtime(self):
        '''returns generator object within range of availble indicies'''
        for i in range(self._get_runtime_idx(self.__start_idx),
                       self.__len__()):
            yield self.__array[i]._get_runtime()

    def __len__(self):
        return self.__length


class StackFrame(KSP):
    '''assigns variables to arr in order of passing.
    kLoc objects become items of an array, or StackFrameArray objects
    depends on their size.
    '''

    def __init__(self, arr: KspArray, variables: tuple,
                 start_idx: KspVar):
        if not isinstance(arr, KspArray):
            raise TypeError(f'arr has to be instance of {KspArray}')
        self.__vars = list()
        idx = 0
        for var in variables:
            if isinstance(var, (int, str, float)):
                arr[idx + start_idx] <<= var
                self.__vars.append(arr[idx + start_idx])
                idx += 1
                continue
            if not isinstance(var, (KspVar, kLoc)):
                raise TypeError('all variables has to be instance of ' +
                                f'{(KspVar, kLoc, int, str, float)}. ' +
                                f'Type of {var} is {type(var)}')
            if isinstance(var, kLoc):
                if var._size > 1:
                    self.__vars.append(StackFrameArray(arr,
                                                       idx + start_idx,
                                                       idx + start_idx +
                                                       var._size))
                    with For(var._size) as seq:
                        for val in seq:
                            arr[val + idx + start_idx] <<= arr.default
                        idx += var._size
                else:
                    arr[idx + start_idx] <<= arr.default
                    self.__vars.append(arr[idx + start_idx])
                    idx += 1
                continue
            if isinstance(var, KspArray):
                self.__vars.append(StackFrameArray(arr,
                                                   idx + start_idx,
                                                   idx + start_idx +
                                                   len(var)))
                with For(len(var)) as seq:
                    for val in seq:
                        arr[val + idx + start_idx] <<= var[val]
                        idx += 1
                continue
            arr[idx + start_idx] <<= var
            self.__vars.append(arr[idx + start_idx])
            idx += 1
        self.__size = idx

    @property
    def vars(self):
        '''returns tuple of array items and StackFrameArray objects
        frame contains'''
        return self.__vars

    @property
    def size(self):
        '''returns int of total length of all items in the frame'''
        return self.__size


class Stack(KSP):
    '''Can hold KSP variables and objecets of types (int, str, float)
    can hold only one type of objects
    '''

    depth = 100

    def __init__(self, name: str,
                 ref_type: (kArrInt, kArrStr, kArrReal),
                 size: int):
        if ref_type not in (kArrInt, kArrStr, kArrReal):
            raise TypeError('ref_type can be only ' +
                            f'{(kArrInt, kArrStr, kArrReal)}')
        prefix = f'_stack_{name}'
        self._arr = ref_type(name=f'{prefix}_arr', size=size)
        self._idx = kArrInt(name=f'{prefix}_idx', size=Stack.depth)
        self._pointer = kInt(-1, f'{prefix}_pointer')
        self._frames = list()
        self._init_lines = list()
        self._init_lines.extend(self._arr._generate_init())
        self._init_lines.extend(self._idx._generate_init())
        self._init_lines.extend(self._pointer._generate_init())

    def push(self, *variables):
        '''puts variables to stack and returns tuple of
        items of self array.
        '''
        self._pointer.inc()
        if self._pointer._get_runtime() > 0:
            self._idx[self._pointer] <<= \
                self._idx[self._pointer - 1] + self._frames[-1].size
        start_idx = self._idx[self._pointer]
        frame = StackFrame(self._arr,
                           variables,
                           start_idx)
        self._frames.append(frame)
        return frame.vars

    def pop(self):
        '''deletes top frame of stack and returns it'''
        out = self._frames.pop()
        self._pointer.dec()
        return out

    def is_empty(self):
        '''returns True if empty'''
        return len(self._frames) == 0


class MultiFrame:
    '''holds bolean attributes:
        is_int
        is_str
        is_real
    for track which stack has to be poped at pop method of MultiStack
    '''

    def __init__(self, _vars, int_count, str_count, real_count):
        self.vars = _vars
        self.is_int = int_count > 0
        self.is_str = str_count > 0
        self.is_real = real_count > 0


class MultiStack(KSP):
    '''the same as Stack, but can keep values of all KSP valid types'''

    def __init__(self, name: str, size: int):
        self._int = Stack(f'{name}_int',
                          ref_type=kArrInt,
                          size=size)
        self._str = Stack(f'{name}_str',
                          ref_type=kArrStr,
                          size=size)
        self._real = Stack(f'{name}_real',
                           ref_type=kArrReal,
                           size=size)
        self._frames = list()
        self._init_lines = self._int._init_lines
        self._init_lines.extend(self._str._init_lines)
        self._init_lines.extend(self._real._init_lines)

    def push(self, *variables):
        '''pushes variables and returns their connected stacks arrays
        items in order of pasting'''
        types = list()
        _int = list()
        _str = list()
        _real = list()
        for var in variables:
            _type = self._get_var_type(var)
            types.append(_type)
            if _type is int:
                _int.append(var)
            if _type is str:
                _str.append(var)
            if _type is float:
                _real.append(var)
        if _int:
            _int = self._int.push(*_int)
        if _str:
            _str = self._str.push(*_str)
        if _real:
            _real = self._real.push(*_real)
        int_count = 0
        str_count = 0
        real_count = 0
        _vars = list()
        for _type in types:
            if _type is int:
                _vars.append(_int[int_count])
                int_count += 1
            if _type is str:
                _vars.append(_str[str_count])
                str_count += 1
            if _type is float:
                _vars.append(_real[real_count])
                real_count += 1
        frame = MultiFrame(_vars, int_count, str_count, real_count)
        self._frames.append(frame)
        return _vars

    @staticmethod
    def _get_var_type(var):
        '''returns int, str or float depends on inut var type'''
        pure_var = var
        if isinstance(var, (list, KspArray)):
            var = var[0]
        if isinstance(var, (KspIntVar, int)):
            return int
        if isinstance(var, (KspRealVar, float)):
            return float
        if isinstance(var, (KspStrVar, str)):
            return str
        if isinstance(var, kLoc):
            if var.ref_type is kInt:
                return int
            if var.ref_type is kStr:
                return str
            if var.ref_type is kReal:
                return float
        raise TypeError(f'can not resolve type for {pure_var}')

    def pop(self):
        '''pop stacks, that have vars in the current frame and
        returns all frame variables'''
        frame = self._frames.pop()
        if frame.is_int:
            self._int.pop()
        if frame.is_str:
            self._str.pop()
        if frame.is_real:
            self._real.pop()
        return frame.vars

    def is_empty(self):
        '''returns True if empty'''
        return len(self._frames) == 0
