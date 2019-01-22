import typing as ty
from abc import abstractmethod

if __name__ == '__main__':
    __name__ = 'pyksp.base_types'

from .abstract import KspObject
from .abstract import NameBase
from .abstract import NameVar
from .abstract import AstRoot
from .abstract import AstString
from .abstract import AstBase
from .abstract import HasInit
from .abstract import KSP
from .abstract import KSPBaseMeta


T = ty.TypeVar('T')
KT = ty.TypeVar('KT', int, float, str)
KVT = ty.TypeVar('KVT', bound='kVar')
NT = ty.TypeVar('NT', int, float)
# AT = ty.TypeVar('AT', bound='kVar[KT]')

ATU = ty.Union['kVar[KT]', 'AstBase[KT]', 'Magic[KT]', KT]
STU = ty.Union['kVar[KT]', 'AstBase[KT]', 'Magic[KT]', str]
NTU = ty.Union['kVar[NT]', 'AstBase[NT]', 'ProcessNum[NT]', NT]
NotVarNTU = ty.Union['AstBase[NT]', 'ProcessNum[NT]', NT]


@ty.overload
def get_value(value: ATU[int]) -> int:
    ...


@ty.overload
def get_value(value: ATU[str]) -> str:
    ...


@ty.overload
def get_value(value: ATU[float]) -> float:
    ...


def get_value(value: ATU[KT]) -> KT:
    if isinstance(value, (int, str, float)):
        return value
    if isinstance(value, kVar):
        return value._value
    if isinstance(value, AstBase):
        return value.get_value()
    raise TypeError(f"Can't infer type of {value}")


@ty.overload
def get_compiled(value: ATU[int]) -> str:
    ...


@ty.overload
def get_compiled(value: ATU[str]) -> str:
    ...


@ty.overload
def get_compiled(value: ATU[float]) -> str:
    ...


def get_compiled(value: ATU[KT]) -> str:
    if isinstance(value, (int, float)):
        return f'{value}'
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, kVar):
        return value.name()
    if isinstance(value, AstBase):
        return value.expand()
    raise TypeError(f"Can't infer type of {value}")


def get_value_type(value: ATU[KT]) -> ty.Type[KT]:
    checked = get_value(value)
    c_type = type(checked)
    if c_type not in (int, str, float):
        raise TypeError(f'can not infer type of {value}')
    return c_type


class Magic(KSP, ty.Generic[KT]):
    pass


class ConcatsStrings(Magic[str]):

    def __add__(self, other: STU) -> 'AstConcatString':
        return AstConcatString(self, other)

    def __radd__(self, other: STU) -> 'AstConcatString':
        return AstConcatString(other, self)


class AstConcatString(AstBase[str], ConcatsStrings):

    def __init__(self, arg1: STU, arg2: STU) -> None:
        for idx, arg in enumerate((arg1, arg2)):
            if not isinstance(arg, STT):
                raise TypeError(f'arg {idx} ({arg}) has ' +
                                f'to be of type {STU}')  # type: ignore
        self._ref_type = str
        self.arg1 = arg1
        self.arg2 = arg2

    def expand(self) -> str:
        return f'{get_compiled(self.arg1)} & {get_compiled(self.arg2)}'

    def get_value(self) -> str:
        return str(get_value(self.arg1)) + str(get_value(self.arg2))

    def __iadd__(self, other: STU) -> ty.NoReturn:
        raise RuntimeError('can not assign to AST object')


FT = ty.TypeVar('FT', bound=ty.Callable[..., ty.Any])


def ducktype_num_magic(method: FT) -> FT:

    def wrpapper(self: 'ProcessNum[NT]', other: NTU[NT]) -> ty.Any:
        other = self._check_for_int(other)  # type: ignore
        value = get_value(other)
        if not isinstance(value, self._ref_type):
            raise TypeError(
                f'incompatible type: {type(other)}'   # type: ignore
                f' -> NT = {self._ref_type}:'
                f' {NTU[self._ref_type]}')   # type: ignore
        return method(self, other)
    return ty.cast(FT, wrpapper)


class ProcessNum(Magic[NT], ty.Generic[NT]):
    _ref_type: ty.Type[NT]

    def _check_for_int(self, other: NTU[NT]) -> ty.Union[NTU[NT], float]:
        if isinstance(other, int) and issubclass(self._ref_type, float):
            return float(other)
        return other

    def __neg__(self) -> 'AstNeg[NT]':
        return AstNeg(self)

    def __invert__(self) -> 'AstNot':
        if not issubclass(self._ref_type, int):
            raise TypeError('can only be apllied to int expression' +
                            f'pasted {self} ({type(self)})')
        return AstNot(self)

    @ducktype_num_magic
    def __add__(self, other: NTU[NT]) -> 'AstAdd[NT]':
        return AstAdd(self, other)

    @ducktype_num_magic
    def __radd__(self, other: NTU[NT]) -> 'AstAdd[NT]':
        return AstAdd(other, self)

    @ducktype_num_magic
    def __sub__(self, other: NTU[NT]) -> 'AstSub[NT]':
        return AstSub(self, other)

    @ducktype_num_magic
    def __rsub__(self, other: NTU[NT]) -> 'AstSub[NT]':
        return AstSub(other, self)

    @ducktype_num_magic
    def __mul__(self, other: NTU[NT]) -> 'AstMul[NT]':
        return AstMul(self, other)

    @ducktype_num_magic
    def __rmul__(self, other: NTU[NT]) -> 'AstMul[NT]':
        return AstMul(other, self)

    @ducktype_num_magic
    def __truediv__(self, other: NTU[NT]) -> 'AstDiv[NT]':
        return AstDiv(self, other)

    @ducktype_num_magic
    def __rtruediv__(self, other: NTU[NT]) -> 'AstDiv[NT]':
        return AstDiv(other, self)

    def __mod__(self, other: NTU[int]) -> 'AstMod':
        if not issubclass(self._ref_type, int):
            raise TypeError('can only be apllied to int expression' +
                            f'pasted {other} ({type(other)})')
        return AstMod(self, other)

    def __rmod__(self, other: NTU[int]) -> 'AstMod':
        if not issubclass(self._ref_type, int):
            raise TypeError('can only be apllied to int expression' +
                            f'pasted {other} ({type(other)})')
        return AstMod(other, self)

    def __pow__(self, other: NTU[float]) -> 'AstPow':
        if not issubclass(self._ref_type, float):
            raise TypeError('can only be apllied to float expression' +
                            f'pasted {other} ({type(other)})')
        return AstPow(self, other)  # type: ignore

    def __rpow__(self, other: NTU[float]) -> 'AstPow':
        if not issubclass(self._ref_type, float):
            raise TypeError('can only be apllied to float expression' +
                            f'pasted {other} ({type(other)})')
        return AstPow(other, self)  # type: ignore

    def __and__(self, other: NTU[NT]) -> 'AstAnd[NT]':
        return AstAnd(self, other)

    def __rand__(self, other: NTU[NT]) -> 'AstAnd[NT]':
        return AstAnd(other, self)

    def __or__(self, other: NTU[NT]) -> 'AstOr[NT]':
        return AstOr(self, other)

    def __ror__(self, other: NTU[NT]) -> 'AstOr[NT]':
        return AstOr(other, self)

    @ducktype_num_magic
    def __eq__(self, other: NTU[NT]) -> 'AstEq[NT]':  # type: ignore
        return AstEq(self, other)

    @ducktype_num_magic
    def __ne__(self, other: NTU[NT]) -> 'AstNe[NT]':  # type: ignore
        return AstNe(self, other)

    @ducktype_num_magic
    def __lt__(self, other: NTU[NT]) -> 'AstLt[NT]':
        return AstLt(self, other)

    @ducktype_num_magic
    def __gt__(self, other: NTU[NT]) -> 'AstGt[NT]':
        return AstGt(self, other)

    @ducktype_num_magic
    def __le__(self, other: NTU[NT]) -> 'AstLe[NT]':
        return AstLe(self, other)

    @ducktype_num_magic
    def __ge__(self, other: NTU[NT]) -> 'AstGe[NT]':
        return AstGe(self, other)

    def __abs__(self) -> 'AstAbs[NT]':
        return AstAbs(self)

    def to_int(self) -> 'AstInt':
        if not issubclass(self._ref_type, float):
            raise TypeError('availble only for KSP float expression')
        return AstInt(self)  # type: ignore

    def to_float(self) -> 'AstFloat':
        if not issubclass(self._ref_type, int):
            raise TypeError('availble only for KSP int expression')
        return AstFloat(self)

    def __lshift__(self, other: NTU[int]) -> 'AstLshift':
        if not issubclass(self._ref_type, int):
            raise TypeError('availble only for KSP int expression')
        return AstLshift(self, other)

    def __rlshift__(self, other: NTU[int]) -> 'AstLshift':
        if not issubclass(self._ref_type, int):
            raise TypeError('availble only for KSP int expression')
        return AstLshift(other, self)

    def __rshift__(self, other: NTU[int]) -> 'AstRshift':
        if not issubclass(self._ref_type, int):
            raise TypeError('availble only for KSP int expression')
        return AstRshift(self, other)

    def __rrshift__(self, other: NTU[int]) -> 'AstRshift':
        if not issubclass(self._ref_type, int):
            raise TypeError('availble only for KSP int expression')
        return AstRshift(other, self)


def to_int(value: ProcessNum) -> 'AstInt':
    return value.to_int()


def to_float(value: ProcessNum) -> 'AstFloat':
    return value.to_float()


# class VarMeta(KSPBaseMeta):

#     def __call__(cls, value: ty.Optional[KT]=None,
#                  *args: ty.Any, **kwargs: ty.Any) -> 'kVar[KT]':
#         if issubclass(cls, Str):
#             cls._arg = str   # type: ignore
#         if value is None and cls._arg is None:
#             raise TypeError('kVar type has to be specified or' +
#                             ' value has to be initialized')
#         if cls._arg:
#             cls._ref = cls._arg
#             if value is None:
#                 # value =
#                 value = ty.cast(KT, cls._ref())
#             elif not isinstance(value, cls._ref):
#                 raise TypeError(
#                     'value has to be of type {ref}, pasted: {val}'.format(
#                         ref=cls._ref, val=value))
#         else:
#             # value = ty.cast(KT, value)
#             cls._ref = get_value_type(value)  # type: ignore
#         if cls is kVar:
#             if cls._ref is str:
#                 obj = Str(value, *args, **kwargs)  # type: ignore
#             else:
#                 obj = Num(value, *args, **kwargs)  # type: ignore
#         else:
#             obj = super().__call__(value, *args, **kwargs)  # type: ignore
#         cls._arg = None   # type: ignore
#         return obj   # type: ignore


class kVar(KspObject, HasInit, ty.Generic[KT]):
    names_count: int = 0
    _arg: ty.ClassVar[ty.Optional[ty.Type[KT]]] = None
    _ref: ty.Type[KT]
    _ref_type: ty.Type[KT]

    # def __class_getitem__(cls,  # type: ignore
    #                       *args: KT,   # type: ignore
    #                       **kwargs: ty.Any   # type: ignore
    #                       ) -> ty.Type['kVar[KT]']:  # type: ignore
    #     cls._arg = args[0]  # type: ignore
    #     return super().__class_getitem__(*args, **kwargs)  # type: ignore

    class Persist:
        """Class for mark persistence of variable.

        can be:
        kVar.not_persistent
        kVar.persistent
        kVar.inst_persistent
        kVar.read_persistent"""

        def __init__(self, line: str='') -> None:
            self.line = line

    not_persistent: ty.ClassVar[Persist] = Persist()
    persistent: ty.ClassVar[Persist] = Persist('make_persistent')
    inst_persistent: ty.ClassVar[Persist] = Persist('make_instr_persistent')
    read_persistent: ty.ClassVar[Persist] = Persist('make_persistent')

    def __init__(self,
                 value: KT,
                 name: str='',
                 persist: Persist=not_persistent,
                 preserve_name: bool=False,
                 *, local: bool=False) -> None:
        if local:
            if not name:
                raise TypeError('local name can not be empty')
            sup_name = NameBase(name)
            has_init = False
        else:
            if not name:
                name = f'kVar{kVar.names_count}'
                kVar.names_count += 1
            sup_name = NameVar(name, preserve=preserve_name)
            has_init = True
        super().__init__(sup_name, has_init=has_init)
        self._ref_type: ty.Type[KT] = self._ref
        self.name.prefix = self._get_type_prefix()
        self._persist: kVar.Persist = persist
        self._after_init(value)

    def _after_init(self, value) -> None:
        self._value: KT = value
        self._init_val: KT = value

    def _get_type_prefix(self) -> str:
        if issubclass(self._ref_type, int):
            return '$'
        elif issubclass(self._ref_type, str):
            return '@'
        elif issubclass(self._ref_type, float):
            return '~'
        else:
            raise TypeError(f"Can't infer type of value")

    @abstractmethod
    def get_decl_line(self) -> ty.List[str]:
        pass

    def generate_init(self) -> ty.List[str]:
        out = self.get_decl_line()
        if self._persist is not self.not_persistent:
            out.append(f'{self._persist.line}({self.name()})')
        if self._persist is self.read_persistent:
            out.append(f'read_persistent_var({self.name()})')

        return out

    @property
    def val(self) -> KT:
        return self._value

    def read(self) -> None:
        self._persist = self.persistent
        out = self.get_out()
        out.put_immediatly(AstString(f'read_persistent_var({self.name()})'))

    @abstractmethod
    def __ilshift__(self: KVT, other: ATU) -> KVT:
        pass

    def copy(self: KVT, name: str, prefix: str, postfix: str) -> KVT:
        obj = self.__class__(self._value, name=name, local=True)
        obj.name.prefix = prefix
        obj.name.postfix = postfix
        return obj

    def _make_copy(self, other: 'kVar[KT]',
                   value: KT, new_type: ty.Type[KVT]) -> KVT:
        name = self.name.name
        prefix = self.name.prefix
        postfix = self.name.postfix
        if isinstance(other, new_type):
            ret_obj = other.copy(name, prefix, postfix)
            ret_obj._value = value
        else:
            ret_obj = new_type(value, name, local=True)
            ret_obj.name.prefix = prefix
            ret_obj.name.postfix = postfix
        ret_obj._init_val = self._init_val

        otpt = self.get_out()
        otpt.put_immediatly(AstAssign(self, other))
        return ret_obj

    @staticmethod
    def refresh() -> None:
        kVar.names_count = 0


reveal_type(kVar)
reveal_type(kVar[int])

STT = (kVar, str, ConcatsStrings)


class Str(kVar[str], ConcatsStrings):

    def __init__(self,
                 value: str='',
                 name: str='',
                 persist: kVar.Persist=kVar.not_persistent,
                 preserve_name: bool=False,
                 *, local: bool=False) -> None:
        if not isinstance(value, str):
            raise TypeError(f'value has to be of str type. Pasted: {value}')
        super().__init__(value=value,
                         name=name,
                         persist=persist,
                         preserve_name=preserve_name,
                         local=local)

    def __ilshift__(self, other: STU) -> 'Str':
        if not isinstance(other, STT):
            raise TypeError('incompatible type for assignement: ' +
                            f'{type(other)} -> {STU}')  # type: ignore
        value = get_value(other)
        if not isinstance(value, str):
            value = f'{value}'
        ret_obj = self._make_copy(other, value, Str)

        return ret_obj

    def get_decl_line(self) -> ty.List[str]:
        out = [f'declare {self.name()}']
        if self._init_val:
            out.append(f'{self.name()} := "{self._init_val}"')
        return out

    def __iadd__(self, other: STU) -> 'Str':  # type: ignore
        return self.__ilshift__(AstConcatString(self, other))


class Num(kVar[NT], ProcessNum[NT]):

    def __init__(self,
                 value: NT,
                 name: str='',
                 persist: kVar.Persist=kVar.not_persistent,
                 preserve_name: bool=False,
                 *, local: bool=False) -> None:
        super().__init__(value=value,
                         name=name,
                         persist=persist,
                         preserve_name=preserve_name,
                         local=local)

    def __ilshift__(self, other: ATU[NT]) -> 'Num[NT]':  # type: ignore
        other = self._check_for_int(other)  # type: ignore
        value = get_value(other)
        if not isinstance(value, self._ref_type):
            raise TypeError(f'assigned to a value of wrong type: {value}')
        ret_obj = self._make_copy(other, value, Num)

        return ret_obj

    def get_decl_line(self) -> ty.List[str]:
        value = ''
        if self._init_val:
            value = f' := {self._init_val}'
        out = [f'declare {self.name()}{value}']
        return out

    @ducktype_num_magic
    def __iadd__(self, other: NTU[NT]) -> 'Num[NT]':  # type: ignore
        return self.__ilshift__(AstAdd(self, other))

    @ducktype_num_magic
    def __isub__(self, other: NTU[NT]) -> 'Num[NT]':  # type: ignore
        return self.__ilshift__(AstSub(self, other))

    @ducktype_num_magic
    def __imul__(self, other: NTU[NT]) -> 'Num[NT]':  # type: ignore
        return self.__ilshift__(AstMul(self, other))

    @ducktype_num_magic
    def __itruediv__(self, other: NTU[NT]) -> 'Num[NT]':  # type: ignore
        return self.__ilshift__(AstDiv(self, other))

    @ducktype_num_magic
    def __imod__(self, other: NTU[int]) -> 'Num[int]':  # type: ignore
        if not issubclass(self._ref_type, int):
            raise TypeError('availble only for KSP int expression')
        return self.__ilshift__(AstMod(self, other))

    @ducktype_num_magic
    def __ipow__(self, other: NTU[float]) -> 'Num[float]':  # type: ignore
        if not issubclass(self._ref_type, float):
            raise TypeError('availble only for KSP float expression')
        return self.__ilshift__(AstPow(self, other))  # type: ignore

    def __iand__(self, other: NTU[NT]) -> ty.NoReturn:
        raise NotImplementedError

    def __ior__(self, other: NTU[NT]) -> ty.NoReturn:
        raise NotImplementedError


def _assert_Num_int(var):
    if not isinstance(var, Num):
        raise TypeError(f'can only be used with {Num[int]}')
    if not issubclass(get_value_type(var), int):
        raise TypeError(f'can only be used with {Num[int]}')


def inc(var: Num[int]) -> None:
    _assert_Num_int(var)
    out = var.get_out()
    out.put_immediatly(AstBuiltInBase(None, 'inc', var))
    var._value += 1


def dec(var: Num[int]) -> None:
    _assert_Num_int(var)
    out = var.get_out()
    out.put_immediatly(AstBuiltInBase(None, 'dec', var))
    var._value -= 1


class AstAssign(AstRoot):

    def __init__(self, to_arg: 'kVar', from_arg: ATU) -> None:
        self.to_arg: 'kVar' = to_arg
        self.from_arg: ATU = from_arg

    def expand(self) -> str:
        to = self.to_arg.name()
        from_str = get_compiled(self.from_arg)
        return f'{to} := {from_str}'

    def get_value(self) -> ty.NoReturn:
        raise self.NullError


class AstBuiltInBase(AstRoot, AstBase[KT]):
    _ref_type: ty.Optional[ty.Type[KT]]
    _value: ty.Optional[KT]
    args: ty.List[str]
    string: str

    def __init__(self,
                 ret_val: ty.Optional[KT],
                 string: str,
                 *args: ATU) -> None:
        if ret_val is not None:
            self._ref_type = get_value_type(ret_val)
        else:
            self._ref_type = None
        self._value: ty.Optional[KT] = ret_val
        self.args: ty.List[str] = list(map(get_compiled, args))
        self.string = string

    def expand(self) -> str:
        return f'{self.string}({", ".join(self.args)})'

    def get_value(self) -> KT:
        if self._value is None:
            raise self.NullError
        return self._value


class AstOperatorUnary(AstBase[NT], ProcessNum[NT]):
    arg1: NTU[NT]
    string: ty.ClassVar[str]
    priority: ty.ClassVar[int]

    def __init__(self, arg1: NTU[NT]) -> None:
        self._ref_type = get_value_type(arg1)
        self.arg1: NTU[NT] = arg1
        self.arg1_pure: NT = get_value(arg1)
        self.arg1_str: str = get_compiled(arg1)


class AstOperatorUnaryStandart(AstOperatorUnary[NT]):

    def expand(self) -> str:
        return f'{self.string}{self.arg1_str}'


class AstOperatorDouble(AstOperatorUnary[NT]):
    arg2: NTU[NT]

    def __init__(self, arg1: NTU[NT], arg2: NTU[NT]) -> None:
        super().__init__(arg1)  # type: ignore
        self.arg2 = arg2
        self.arg2_pure: NT = get_value(arg2)
        self.arg2_str: str = get_compiled(arg2)


class AstOperatorDoubleStandart(AstOperatorDouble[NT]):

    def _expand_with_string(self, string: str, is_bool: bool=False) -> str:
        pr: ty.List[int] = list()
        for arg in (self.arg1, self.arg2):
            if isinstance(arg, AstOperatorUnary):
                pr.append(arg.priority)
                continue
            pr.append(0)
        if self.priority <= pr[1]:
            self.arg2_str = f'({self.arg2_str})'
        if self.priority < pr[0]:
            self.arg1_str = f'({self.arg1_str})'
        return f'{self.arg1_str} {string} {self.arg2_str}'

    def expand(self) -> str:
        return self._expand_with_string(self.string)


class AstOperatorUnaryBracket(AstOperatorUnary[NT]):

    def expand(self) -> str:
        return f'{self.string}({self.arg1_str})'


class AstOperatorDoubleBracket(AstOperatorDouble[NT]):

    def expand(self) -> str:
        return f'{self.string}({self.arg1_str}, {self.arg2_str})'


class AstBool(AstBase[NT]):

    @abstractmethod
    def __bool__(self) -> bool:
        pass


def _check_if_bool(arg: NTU[NT]) -> ty.Union[NT, bool]:
    if isinstance(arg, AstBool):
        return arg is True
    return get_value(arg)


class AstCanBeBool(AstOperatorDoubleStandart[NT], AstBool[NT]):
    string_bool: ty.ClassVar[str]
    arg1_pure: ty.Union[NT, bool]
    arg2_pure: ty.Union[NT, bool]

    def __init__(self, arg1: NTU[NT], arg2: NTU[NT]) -> None:
        if isinstance(arg1, AstBool):
            self._ref_type = bool
        else:
            self._ref_type = get_value_type(arg1)
        self.arg1 = arg1
        self.arg1_pure = _check_if_bool(arg1)
        if isinstance(self.arg1, AstCanBeBool):
            self.arg1_str: str = arg1.expand_bool()
        else:
            self.arg1_str = get_compiled(arg1)
        self.arg2 = arg2
        self.arg2_pure: NT = _check_if_bool(arg2)
        if isinstance(self.arg2, AstCanBeBool):
            self.arg2_str: str = arg2.expand_bool()
        else:
            self.arg2_str = get_compiled(arg2)

    def expand(self) -> str:
        if self.is_bool():
            return self.expand_bool()
        return super().expand()

    def expand_bool(self) -> str:
        return self._expand_with_string(self.string_bool, is_bool=True)


class AstNeg(AstOperatorUnaryStandart[NT]):
    priority = 2
    string = '-'

    def get_value(self) -> NT:
        return -self.arg1_pure


class AstNot(AstOperatorUnaryStandart[int]):
    priority = 2
    string = '.not.'

    def get_value(self) -> int:
        if not issubclass(self._ref_type, int):
            raise TypeError('works only on ints')
        return ~self.arg1_pure


class AstAbs(AstOperatorUnaryBracket[NT]):
    priority = 2
    string = 'abs'

    def get_value(self) -> NT:
        return abs(self.arg1_pure)


class AstInt(AstOperatorUnaryBracket[int]):
    priority = 2
    string = 'real_to_int'
    arg1: NTU[float]
    arg1_pure: int
    arg1_str: str

    def __init__(self, arg1: NTU[float]) -> None:
        self._ref_type = int
        self.arg1: NTU[float] = arg1
        self.arg1_pure: int = int(get_value(arg1))
        self.arg1_str: str = get_compiled(arg1)

    def get_value(self) -> int:  # type: ignore
        return int(self.arg1_pure)


class AstFloat(AstOperatorUnaryBracket[float]):
    priority = 2
    string = 'int_to_real'
    arg1: NTU[int]
    arg1_pure: float
    arg1_str: str

    def __init__(self, arg1: NTU[int]) -> None:
        self._ref_type = float
        self.arg1: NTU[int] = arg1
        self.arg1_pure: float = float(get_value(arg1))
        self.arg1_str: str = get_compiled(arg1)

    def get_value(self) -> float:  # type: ignore
        return float(self.arg1_pure)


class AstAdd(AstOperatorDoubleStandart[NT]):
    priority = 4
    string = '+'

    def get_value(self) -> NT:
        return self.arg1_pure + self.arg2_pure


class AstSub(AstOperatorDoubleStandart[NT]):
    priority = 4
    string = '-'

    def get_value(self) -> NT:
        return self.arg1_pure - self.arg2_pure


class AstDiv(AstOperatorDoubleStandart[NT]):
    priority = 3
    string = '/'

    def get_value(self) -> NT:
        try:
            if isinstance(self.arg1_pure, int):
                return self.arg1_pure // self.arg2_pure
            else:
                return self.arg1_pure / self.arg2_pure
        except ZeroDivisionError:
            return 0


class AstMul(AstOperatorDoubleStandart[NT]):
    priority = 3
    string = '*'

    def get_value(self) -> NT:
        return self.arg1_pure * self.arg2_pure


class AstMod(AstOperatorDoubleStandart[int]):
    priority = 3
    string = 'mod'

    def get_value(self) -> int:
        return self.arg1_pure % self.arg2_pure


class AstPow(AstOperatorDoubleBracket[float]):
    priority = 1
    string = 'pow'

    def get_value(self) -> float:
        return self.arg1_pure ** self.arg2_pure


class AstLshift(AstOperatorDoubleBracket[int]):
    priority = 5
    string = 'sh_left'

    def get_value(self) -> int:
        return self.arg1_pure << self.arg2_pure


class AstRshift(AstOperatorDoubleBracket[int]):
    priority = 5
    string = 'sh_right'

    def get_value(self) -> int:
        return self.arg1_pure >> self.arg2_pure


class AstAnd(AstCanBeBool[NT]):
    priority = 7
    string = '.and.'
    string_bool = 'and'

    def get_value(self) -> NT:
        if not issubclass(self._ref_type, int):
            raise TypeError('waorks only on ints')
        return self.arg1_pure & self.arg2_pure

    def __bool__(self) -> bool:
        if self.arg1 and self.arg2:
            return True
        return False


class AstOr(AstCanBeBool[NT]):
    priority = 8
    string = '.or.'
    string_bool = 'or'

    def get_value(self) -> NT:
        if not issubclass(self._ref_type, int):
            raise TypeError('waorks only on ints')
        return self.arg1_pure | self.arg2_pure

    def __bool__(self) -> bool:
        if self.arg1 or self.arg2:
            return True
        return False


class OperatorComparisson(AstOperatorDoubleStandart[NT], AstBool[NT]):

    def expand(self) -> str:
        is_set = False
        if not self.is_bool():
            is_set = True
            self.set_bool(True)
        ret = super().expand()
        if is_set:
            self.set_bool(False)
        return ret

    def get_value(self) -> ty.NoReturn:
        raise NotImplementedError


class AstEq(OperatorComparisson[NT]):
    priority = 6
    string = '='

    def __bool__(self) -> bool:
        if self.arg1_pure == self.arg2_pure:
            return True
        return False


class AstNe(OperatorComparisson[NT]):
    priority = 6
    string = '#'

    def __bool__(self) -> bool:
        if self.arg1_pure != self.arg2_pure:
            return True
        return False


class AstLt(OperatorComparisson[NT]):
    priority = 6
    string = '<'

    def __bool__(self) -> bool:
        if self.arg1_pure < self.arg2_pure:
            return True
        return False


class AstGt(OperatorComparisson[NT]):
    priority = 6
    string = '>'

    def __bool__(self) -> bool:
        if self.arg1_pure > self.arg2_pure:
            return True
        return False


class AstLe(OperatorComparisson[NT]):
    priority = 6
    string = '<='

    def __bool__(self) -> bool:
        if self.arg1_pure <= self.arg2_pure:
            return True
        return False


class AstGe(OperatorComparisson[NT]):
    priority = 6
    string = '>='

    def __bool__(self) -> bool:
        if self.arg1_pure >= self.arg2_pure:
            return True
        return False


class Arr(kVar, ty.Generic[KT]):

    def __init__(self,
                 value: ty.Union[KT, ty.List[KT]],
                 name: str='',
                 persist: kVar.Persist=kVar.not_persistent,
                 preserve_name: bool=False,
                 size: ty.Optional[int]=None, *,
                 local: bool=False) -> None:
        if not isinstance(value, ty.List):
            if size is not None:
                lth = size
            else:
                lth = 1
            value = list([value] * lth)
            self._init_seq = [value]
        super().__init__(value=value,
                         name=name,
                         persist=persist,
                         preserve_name=preserve_name,
                         local=local)

    def _get_type_prefix(self) -> str:
        if issubclass(self._ref_type, int):
            return '%'
        if issubclass(self._ref_type, str):
            return '!'
        if issubclass(self._ref_type, float):
            return '?'

    def get_decl_line(self) -> ty.List[str]:
        ...

    def __ilshift__(self, other: ATU[KT]) -> ty.NoReturn:
        raise NotImplementedError


Num[int](value=0.0)
a: int
a = 's'
