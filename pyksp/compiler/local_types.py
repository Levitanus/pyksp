import numpy as np
from typing import Iterable
# from typing import Sequence

from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal
from native_types import KspNativeArray

# from interfaces import IOutput
from interfaces import INameLocal
# from pyksp_ast import AstGetItem
# from pyksp_ast import AstSetItem


class KspLocal:
    pass


class kLocInt(kInt, KspLocal):

    def __init__(self, name, value):
        self.ref_type = (int, kInt)
        self._value = value
        self.name = INameLocal(name)
        self.name.prefix = '$'

    def _generate_init(self):
        return []


class kLocStr(kStr, KspLocal):

    def __init__(self, name, value):
        self.ref_type = (str, kStr)
        self._value = value
        self.name = INameLocal(name)
        self.name.prefix = '@'

    def _generate_init(self):
        return []


class kLocReal(kReal, KspLocal):

    def __init__(self, name, value):
        self.ref_type = (float, kReal)
        self._value = value
        self.name = INameLocal(name)
        self.name.prefix = '~'

    def _generate_init(self):
        return []


class kLocArrInt(kArrInt, KspLocal):

    def __init__(self, name: str, sequence: Iterable=None,
                 length: int=None):
        self.ref_type = (int, kInt)
        if not sequence and not length:
            raise KspNativeArray.error(
                'length has to be specified or sequence passed')
        self.length = length
        if not length:
            self.length = len(sequence)

        self.seq = np.zeros(self.length, kLocInt)
        if sequence:
            if not isinstance(sequence, Iterable):
                raise TypeError('sequence has to be iterable')
            for idx, val in enumerate(sequence):
                self.seq[idx] = val
        self._value = sequence
        self.name = INameLocal(name)
        self.name.prefix = '%'

    def _generate_init(self):
        return []


class kLocArrStr(kArrStr, KspLocal):

    def __init__(self, name: str, sequence: Iterable=None,
                 length: int=None):
        self.ref_type = (str, kStr)
        if not isinstance(sequence, Iterable):
            raise TypeError('sequence has to be iterable')
        if not sequence and not length:
            raise KspNativeArray.error(
                'length has to be specified or sequence passed')
        self.length = length
        if not length:
            self.length = len(sequence)

        self.seq = np.zeros(self.length, kStr)
        if sequence:
            for idx, val in enumerate(sequence):
                self.seq[idx] = val
        self._value = sequence
        self.name = INameLocal(name)
        self.name.prefix = '!'

    def _generate_init(self):
        return []


class kLocArrReal(kArrReal, KspLocal):

    def __init__(self, name: str, sequence: Iterable=None,
                 length: int=None):
        self.ref_type = (float, kReal)
        if not isinstance(sequence, Iterable):
            raise TypeError('sequence has to be iterable')
        if not sequence and not length:
            raise KspNativeArray.error(
                'length has to be specified or sequence passed')
        self.length = length
        if not length:
            self.length = len(sequence)

        self.seq = np.zeros(self.length, kReal)
        if sequence:
            for idx, val in enumerate(sequence):
                if not isinstance(val, self.ref_type):
                    raise \
                        TypeError(
                            f'item at idx {idx} is {type(val)}.' +
                            f' Has to be one of {self.ref_type}')
                self.seq[idx] = val
        self._value = sequence
        self.name = INameLocal(name)
        self.name.prefix = '?'

    def _generate_init(self):
        return []
