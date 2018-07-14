import numpy as np

from kspvar import KspVarObj
from typing import Iterable
from interfaces import IOutput
from abstract import KSP

from pyksp_ast import *

IGNORE = 1
ONLY_NAME = 2
WHOLE = 3


class KspNative(KspVarObj):
    '''Base class for native KSP objects:
        - variables
        - arrays
    '''

    def __init__(self, value, name: str, prefix: str,
                 ref_type=None,
                 preserve_name: bool=False, persist: bool = False):
        super().__init__(name, value, preserve_name)
        self.init_value = self.value_get()
        self.name.prefix = prefix
        self.persist = persist
        self.ref_type = ref_type
        self.init_mode = WHOLE

    def value_set(self, value):
        if self.is_under_test():
            if not isinstance(value, self.ref_type):
                raise TypeError("You've tried to assign %s."
                                "Has to be one of %s" %
                                (type(value), self.ref_type))
        super().value_set(value)

    def _generate_init(self):
        if self.init_mode == IGNORE:
            return []
        init_lines = list()
        decl_line = '%s' % self.name()
        if self.init_mode != ONLY_NAME:
            decl_line = 'declare %s' % decl_line
        if self.init_value:
            decl_line += ' := %s' % self.init_value
        init_lines.append(decl_line)
        if self.persist:
            init_lines.append('make_persistent(%s)' % self.name())
        return init_lines


class kInt(KspNative):
    '''native integer variable ($var)'''

    def __init__(self, name: str, value: int=0,
                 preserve_name: bool=False, persist: bool = False):
        if not isinstance(value, int):
            raise TypeError('value has to be int')
        super().__init__(value, name, '$', (int, kInt),
                         preserve_name, persist)

    def __index__(self):
        return self.__call__()


class kStr(KspNative):
    '''native integer variable (@var)'''

    def __init__(self, name: str, value: str='',
                 preserve_name: bool=False, persist: bool = False):
        if not isinstance(value, str):
            raise TypeError('value has to be str')
        super().__init__(value, name, '@', (str, kStr),
                         preserve_name, persist)

    def value_set(self, value):
        if isinstance(value, (kInt, kReal)):
            value = '%s' % value.value_get()
        super().value_set(value)

    def convert_to_str(self, value):
        if isinstance(value, (KspVarObj)):
            return '%s' % value()
        if not isinstance(value, str):
            raise TypeError('String Var can accept only str, and ksp,'
                            ' objects. You passed %s' % type(value))
        return value

    def __add__(self, other):
        other = self.convert_to_str(other)
        if self.is_under_test():
            return self.value_get() + other
        return '%s & %s' % (self.name(), other)

    def __radd__(self, other):
        other = self.convert_to_str(other)
        if self.is_under_test():
            return other + self.value_get()
        return '%s & %s' % (other, self.name())

    def __iadd__(self, other):
        other = self.convert_to_str(other)
        self.value_set(self._value + other)
        if not self.is_under_test():
            self._ast_assign('%s & %s' % (self.name(), other))
        return self


class kReal(KspNative):
    '''native real variable (~var)'''

    def __init__(self, name: str, value: int=0,
                 preserve_name: bool=False, persist: bool=False):
        super().__init__(value, name, '~', preserve_name, persist)


class KspNativeArray(KspNative):
    '''Base class for native KSP arrays.
    can not be iterated.

    TODO:
        - extend and append have to return Ast methods
        - extend and append has to raise exception inside functions
    '''

    def __init__(self, value: Iterable, name: str, prefix: str,
                 ref_type: type=None, length: int=False,
                 preserve_name: bool=False, persist: bool = False) -> None:
        self.init_length = length
        self.ref_type = ref_type
        self.seq = list()
        if length:
            self.seq = np.zeros(length, ref_type[1])
        if value:
            for idx, val in enumerate(value):
                if length:
                    self.seq[idx] = val
                continue
            self.seq = value
        if not isinstance(value, Iterable):
            raise TypeError('value has to be iterable')
        super().__init__(1, name, prefix,
                         ref_type, preserve_name, persist)
        self.init_value = value

    def _get_ref_type(self, value):
        if not isinstance(value, self.ref_type):
            raise TypeError('object is %s, has to be %s' %
                            (type(value), self.ref_type))
        if isinstance(value, int):
            cls = kInt
        if isinstance(value, str):
            cls = kStr
        if isinstance(value, float):
            cls = kReal
        if isinstance(value, KspNative):
            cls = type(value)
            value = value.value_get()
        return cls, value

    def __getitem__(self, idx):
        # print('native get')
        if self.is_under_test():
            if callable(self.seq[idx]):
                return self.seq[idx]()
            return self.seq[idx]
        return AstGetItem(self, idx)

    def __setitem__(self, idx, val):
        # print('native set',
        #       f'ref_type is {self.ref_type}')
        if self.is_under_test():
            # print('val type = %s, ref_type = %s' % (
            #     type(val), self.ref_type))
            if not isinstance(val, self.ref_type):
                raise \
                    TypeError(
                        f'item at idx {idx} is {type(val)}.' +
                        f' Has to be one of {self.ref_type}')
            self.seq[idx] = val
            return
        IOutput.put(AstSetItem(self, idx, val)())
        return

    def __len__(self):
        return len(self.seq)

    class error(TypeError):
        pass

    def __iter__(self):
        # print('native iter')
        if not KSP.is_under_test():
            raise self.error(
                'for using KSP array in for loop use For() object')
        return iter(self.seq)

    def __call__(self):
        if KSP.is_under_test():
            return self.seq
        return self.name()

    def value_get(self):
        return self.seq

    def append(self, value):
        if self.init_length:
            raise self.error('can not append to fixed-sized array')
        if not isinstance(value, self.ref_type):
            raise TypeError(
                'has to be one of %s, passed %s' % (
                    self.ref_type, type(value)))
        if not KSP.is_under_test():
            IOutput.put(f'{self.name()}[{len(self.seq)}] := ' +
                        f'{value}')
        self.seq.append(value)

    def extend(self, sequence):
        for val in sequence:
            self.seq.append(val)

    def _generate_init(self):
        init_lines = []
        length = len(self.seq)
        if self.init_length:
            length = self.init_length
        decl_line = 'declare %s[%s]' % (self.name(), length)
        init_lines.append(decl_line)
        if self.persist:
            init_lines.append('make_persistent(%s)' % self.name())
        if self.init_value:
            multiline = False
            out = list()
            for idx, item in enumerate(self.init_value):
                if multiline:
                    multiline.append((item, idx))
                    continue
                if isinstance(item, KspNative):
                    if multiline:
                        multiline.append((item(), idx))
                        continue
                    multiline = [(item(), idx)]
                    continue
                val = ''
                if idx != 0:
                    val = ', '
                val += str(item)
                out.append(val)
            if len(out) > 0:
                val = ''
                for x in out:
                    val += x
                decl_line += ' := (%s)' % val
            init_lines[0] = decl_line
            if multiline:
                for idx, val in enumerate(multiline):
                    multiline[idx] = '%s[%s] := %s' % (self.name(),
                                                       val[1], val[0])
                init_lines.extend(multiline)
        return init_lines


class kArrInt(KspNativeArray):
    '''native integer array (%arr[])'''

    def __init__(self, name: str, sequence: Iterable[int]=[],
                 length=False,
                 preserve_name: bool=False, persist: bool=False):
        super().__init__(sequence, name, '%', (int, kInt),
                         length, preserve_name, persist)


class kArrStr(KspNativeArray):
    '''native string array (!arr[])'''

    def __init__(self, name: str, sequence: Iterable[str]=[],
                 length=False,
                 preserve_name: bool=False, persist: bool=False):
        super().__init__(sequence, name, '!', (str, kStr),
                         length, preserve_name, persist)

    def append(self, value):
        if isinstance(value, kInt):
            value = str(value())
        super().append(value)

    def __setitem__(self, idx, val):
        if self.is_under_test():
            if isinstance(val, (int, kInt)):
                val = f'{val}'
            self.seq[idx] = val
            return
        if isinstance(val, str):
            val = f'"{val}"'
        IOutput.put(AstSetItem(self, idx, val)())
        return


class kArrReal(KspNativeArray):
    '''native real array (?arr[])'''

    def __init__(self, name: str, sequence: Iterable[float]=[],
                 length=False,
                 preserve_name: bool=False, persist: bool=False):
        super().__init__(sequence, name, '?', (float, kReal),
                         length, preserve_name, persist)


class kVar:

    __count = 0

    def __new__(cls, value, name: str=None, preserve_name: bool=False,
                persist: bool = False, length: int=False):
        if name is None:
            name = f'var{kVar.__count}'
            kVar.__count += 1
        args = {
            'name': name,
            'value': value,
            'preserve_name': preserve_name,
            'persist': persist
        }
        length_err_msg = f'{type(value)} object can not have length'
        if isinstance(value, (int, kInt)):
            if length:
                raise kVar.error(length_err_msg)
            return kInt(**args)
        if isinstance(value, (str, kStr)):
            if length:
                raise kVar.error(length_err_msg)
            return kStr(**args)
        if isinstance(value, (float, kReal)):
            if length:
                raise kVar.error(length_err_msg)
            return kReal(**args)
        try:
            ref_type = value[0]
        except TypeError:
            raise kVar.error("can't resolve variable type")
        args['length'] = length
        del args['value']
        args['sequence'] = value
        for val in value:
            if not isinstance(val, type(ref_type)):
                raise kVar.error(
                    "elements in sequence are of different types")
        if isinstance(ref_type, (int, kInt)):
            return kArrInt(**args)
        if isinstance(ref_type, (str, kStr)):
            return kArrStr(**args)
        if isinstance(ref_type, (float, kReal)):
            return kArrReal(**args)
        raise kVar.error("can't resolve variable type")

    class error(Exception):
        pass
