"""Base KSP types and compiler mechanics."""  # type: ignore
import typing as ty
from abc import abstractmethod

from .abstract import KspObject
from .abstract import NameBase
from .abstract import NameVar
from .abstract import AstRoot
from .abstract import AstString
from .abstract import AstBase
from .abstract import HasInit
from .abstract import KSP
from .abstract import KSPBaseMeta

T = ty.TypeVar("T")
KT = ty.TypeVar("KT", int, float, str)
KVT = ty.TypeVar("KVT", bound="VarParent")
NT = ty.TypeVar("NT", int, float)
KTT = (int, str, float)
# AT = ty.TypeVar('AT', bound='VarParent[KT]')

ATU = ty.Union["VarParent[KT]", "AstBase[KT]", "Magic[KT]", KT]
STU = ty.Union["VarParent[KT]", "AstBase[KT]", "Magic[KT]", str]
NTU = ty.Union["VarParent[NT]", "ProcessNum[NT]", NT]
NotVarNTU = ty.Union["AstBase[NT]", "ProcessNum[NT]", NT]


def get_value(value: ATU[KT]) -> KT:
    """Retrieve realtime value of object."""
    if isinstance(value, (int, str, float)):
        return value
    if isinstance(value, VarParent):
        return value.val
    if isinstance(value, AstBase):
        return value.get_value()
    raise TypeError(f"Can't infer type of {value}")


def get_compiled(value: ATU[KT]) -> str:
    """Retrive KSP representation of object."""
    if isinstance(value, (int, float)):
        return f"{value}"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, VarParent):
        return value.name()
    if isinstance(value, AstBase):
        return value.expand()
    raise TypeError(f"Can't infer type of {value}")


def get_value_type(value: ATU[KT]) -> ty.Type[KT]:
    """Retrive generic reference type of object.

    e.g. int, str, float"""
    checked = get_value(value)
    c_type = type(checked)
    if c_type not in (int, str, float):
        raise TypeError(f"can not infer type of {value}")
    return c_type


class Magic(KSP, ty.Generic[KT]):
    """Base class for types with magic methods."""


class ConcatsStrings(Magic[str]):
    """Supports str, ConcatStr and any Var objects concatenation."""

    def __add__(self, other: STU) -> "AstConcatString":
        """Return AstConcatString object."""
        return AstConcatString(self, other)

    def __radd__(self, other: STU) -> "AstConcatString":
        """Return AstConcatString object."""
        return AstConcatString(other, self)


class AstConcatString(AstBase[str], ConcatsStrings):
    """Ast, handles strings concatenation."""

    def __init__(self, arg1: STU, arg2: STU) -> None:  # pylint: disable=W0231
        """Accept args and initialize ref_type."""
        for idx, arg in enumerate((arg1, arg2)):
            if not isinstance(arg, STT):
                raise TypeError(f"arg {idx} ({arg}) has " +
                                f"to be of type {STU}"  # type: ignore
                                )
        self._ref_type = str
        self.arg1 = arg1
        self.arg2 = arg2

    def expand(self) -> str:
        """Return KSP string representation."""
        return f"{get_compiled(self.arg1)} & {get_compiled(self.arg2)}"

    def get_value(self) -> str:
        """Return concatenated string."""
        return str(get_value(self.arg1)) + str(get_value(self.arg2))

    def __iadd__(self, other: STU) -> ty.NoReturn:
        """Not implemented."""
        raise RuntimeError("can not assign to AST object")


FT = ty.TypeVar("FT", bound=ty.Callable[..., ty.Any])


def ducktype_num_magic(method: FT) -> FT:
    """Check that ref_type of other is campatible with self."""

    def wrpapper(self: "ProcessNum[NT]", other: NTU[NT]) -> ty.Any:
        other = self._check_for_int(other)  # type: ignore
        value = get_value(other)
        if not isinstance(value, self._ref_type):
            raise TypeError(f"incompatible type: {type(other)}"  # type: ignore
                            f" -> NT = {self._ref_type}:"
                            f" {NTU[self._ref_type]}")
        return method(self, other)

    return ty.cast(FT, wrpapper)


class ProcessNum(Magic[NT], ty.Generic[NT]):
    """Base class for objects, keeps int and float values."""

    _ref_type: ty.Type[NT]

    def _check_for_int(self, other: NTU[NT]) -> ty.Union[NTU[NT], float]:
        """Convert int to float if self._ref_type is float."""
        if isinstance(other, int) and issubclass(self._ref_type, float):
            return float(other)
        return other

    def __neg__(self) -> "AstNeg[NT]":
        """Return AstNeg object."""
        return AstNeg(self)

    def __invert__(self) -> "AstNot":
        """Return AstNot object if self ref is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("can only be apllied to int expression" +
                            f"pasted {self} ({type(self)})")
        return AstNot(self)  # type: ignore

    @ducktype_num_magic
    def __add__(self, other: NTU[NT]) -> "AstAdd[NT]":
        """Return AstAdd[self._ref_type] object."""
        return AstAdd(self, other)

    @ducktype_num_magic
    def __radd__(self, other: NTU[NT]) -> "AstAdd[NT]":
        """Return AstAdd[self._ref_type] object."""
        return AstAdd(other, self)

    @ducktype_num_magic
    def __sub__(self, other: NTU[NT]) -> "AstSub[NT]":
        """Return AstSub[self._ref_type] object."""
        return AstSub(self, other)

    @ducktype_num_magic
    def __rsub__(self, other: NTU[NT]) -> "AstSub[NT]":
        """Return AstSub[self._ref_type] object."""
        return AstSub(other, self)

    @ducktype_num_magic
    def __mul__(self, other: NTU[NT]) -> "AstMul[NT]":
        """Return AstMul[self._ref_type] object."""
        return AstMul(self, other)

    @ducktype_num_magic
    def __rmul__(self, other: NTU[NT]) -> "AstMul[NT]":
        """Return AstMul[self._ref_type] object."""
        return AstMul(other, self)

    @ducktype_num_magic
    def __truediv__(self, other: NTU[NT]) -> "AstDiv[NT]":
        """Return AstDiv[self._ref_type] object."""
        return AstDiv(self, other)

    @ducktype_num_magic
    def __rtruediv__(self, other: NTU[NT]) -> "AstDiv[NT]":
        """Return AstDiv[self._ref_type] object."""
        return AstDiv(other, self)

    def __mod__(self, other: NTU[int]) -> "AstMod":
        """Return AstMod object if self._ref_type is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("can only be apllied to int expression" +
                            f"pasted {other} ({type(other)})")
        return AstMod(self, other)  # type: ignore

    def __rmod__(self, other: NTU[int]) -> "AstMod":
        """Return AstMod object if self._ref_type is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("can only be apllied to int expression" +
                            f"pasted {other} ({type(other)})")
        return AstMod(other, self)  # type: ignore

    def __pow__(self, other: NTU[float]) -> "AstPow":
        """Return AstPow object if self._ref_type is float."""
        if not issubclass(self._ref_type, float):
            raise TypeError("can only be apllied to float expression" +
                            f"pasted {other} ({type(other)})")
        return AstPow(self, other)  # type: ignore

    def __rpow__(self, other: NTU[float]) -> "AstPow":
        """Return AstPow object if self._ref_type is float."""
        if not issubclass(self._ref_type, float):
            raise TypeError("can only be apllied to float expression" +
                            f"pasted {other} ({type(other)})")
        return AstPow(other, self)  # type: ignore

    def __and__(self, other: NTU[NT]) -> "AstAnd[NT]":
        """Return AstAnd[self._ref_type] object."""
        return AstAnd(self, other)

    def __rand__(self, other: NTU[NT]) -> "AstAnd[NT]":
        """Return AstAnd[self._ref_type] object."""
        return AstAnd(other, self)

    def __or__(self, other: NTU[NT]) -> "AstOr[NT]":
        """Return AstOr[self._ref_type] object."""
        return AstOr(self, other)

    def __ror__(self, other: NTU[NT]) -> "AstOr[NT]":
        """Return AstOr[self._ref_type] object."""
        return AstOr(other, self)

    @ducktype_num_magic
    def __eq__(self, other: NTU[NT]) -> "AstEq[NT]":  # type: ignore
        """Return AstEq object.

        note: AstEq is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstEq)"""
        return AstEq(self, other)

    @ducktype_num_magic
    def __ne__(self, other: NTU[NT]) -> "AstNe[NT]":  # type: ignore
        """Return AstNe object.

        note: AstNe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstNe)"""
        return AstNe(self, other)

    @ducktype_num_magic
    def __lt__(self, other: NTU[NT]) -> "AstLt[NT]":
        """Return AstLt object.

        note: AstLt is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstLt)"""
        return AstLt(self, other)

    @ducktype_num_magic
    def __gt__(self, other: NTU[NT]) -> "AstGt[NT]":
        """Return AstGt object.

        note: AstGt is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstGt)"""
        return AstGt(self, other)

    @ducktype_num_magic
    def __le__(self, other: NTU[NT]) -> "AstLe[NT]":
        """Return AstLe object.

        note: AstLe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstLe)"""
        return AstLe(self, other)

    @ducktype_num_magic
    def __ge__(self, other: NTU[NT]) -> "AstGe[NT]":
        """Return AstGe object.

        note: AstGe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstGe)"""
        return AstGe(self, other)

    def __abs__(self) -> "AstAbs[NT]":
        """Return AstAbs[self._ref_type] object."""
        return AstAbs(self)

    def to_int(self) -> "AstInt":
        """Return AstInt object if self._ref_type is float."""
        if not issubclass(self._ref_type, float):
            raise TypeError("availble only for KSP float expression")
        return AstInt(self)  # type: ignore

    def to_float(self) -> "AstFloat":
        """Return AstFloat object if self._ref_type is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("availble only for KSP int expression")
        return AstFloat(self)  # type: ignore

    def __lshift__(self, other: NTU[int]) -> "AstLshift":
        """Return AstLshift object if self._ref_type is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("availble only for KSP int expression")
        return AstLshift(self, other)  # type: ignore

    def __rlshift__(self, other: NTU[int]) -> "AstLshift":
        """Return AstLshift object if self._ref_type is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("availble only for KSP int expression")
        return AstLshift(other, self)  # type: ignore

    def __rshift__(self, other: NTU[int]) -> "AstRshift":
        """Return AstRshift object if self._ref_type is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("availble only for KSP int expression")
        return AstRshift(self, other)  # type: ignore

    def __rrshift__(self, other: NTU[int]) -> "AstRshift":
        """Return AstRshift object if self._ref_type is int."""
        if not issubclass(self._ref_type, int):
            raise TypeError("availble only for KSP int expression")
        return AstRshift(other, self)  # type: ignore


def to_int(value: ProcessNum) -> "AstInt":
    """Return AstInt object if value._ref_type is float."""
    return value.to_int()


def to_float(value: ProcessNum) -> "AstFloat":
    """Return AstFloat object if value._ref_type is int."""
    return value.to_float()


class VarMeta(KSPBaseMeta):
    """Big Scary metaclass."""

    def __getitem__(cls, *args: ty.Type[KT],
                    **kwargs: ty.Any) -> ty.Type["VarParent[KT]"]:
        """Next class initialization will be infered as passed type."""
        VarParent._ref = args[0]  # type: ignore
        return cls  # type: ignore


class TypeMeta(type):
    """Metaclass for simplifying instance-check."""

    def __instancecheck__(cls, instance: "VarParent") -> bool:
        if isinstance(instance, Arr):
            if not issubclass(cls, TypeArr):
                return False
            if issubclass(instance._ref_type, cls._ref_type):  # type: ignore
                if (cls._size is False or  # type: ignore
                        len(instance) >= cls._size):  # type: ignore
                    return True
            return False
        if not isinstance(instance, VarParent):
            return False
        if issubclass(instance._ref_type, cls._ref_type):  # type: ignore
            return True
        return super().__instancecheck__(instance)

    def __getitem__(
            cls,
            ref: ty.Union[ty.Type[KT], ty.Tuple[ty.Type[KT], ty.
                                                Union[int, bool]]],
    ) -> ty.Type["Type"]:
        if ref is int:
            return TypeInt
        if ref is str:
            return TypeStr
        if ref is float:
            return TypeFloat
        if not isinstance(ref, tuple):
            raise TypeError(f"can't infer type of {ref}")
        if ref[1] is True or ref[1] is None or ref[1] < 0:
            raise TypeError("size par can be only False or positive int")
        if ref[0] is int:
            TypeArrInt._size = ref[1]
            return TypeArrInt
        if ref[0] is str:
            TypeArrStr._size = ref[1]
            return TypeArrStr
        if ref[0] is float:
            TypeArrFloat._size = ref[1]
            return TypeArrFloat
        raise TypeError(f"can't infer type of {ref}")


class Type(metaclass=TypeMeta):
    """Base Var class for instance-checking."""
    _ref_type: ty.Type[ty.Union[int, str, float]]


class TypeInt(Type):
    """IntVar class for instance-checking."""
    _ref_type = int


class TypeStr(Type):
    """StrVar class for instance-checking."""
    _ref_type = str


class TypeFloat(Type):
    """FloatVar class for instance-checking."""
    _ref_type = float


class TypeArr(Type):
    """Base Arr class for instance-checking."""
    _ref_type: ty.Type[ty.Union[int, str, float]]
    _size: ty.Optional[int]


class TypeArrInt(TypeArr):
    """IntArr class for instance-checking."""
    _ref_type = int
    _size: ty.Optional[int] = None


class TypeArrStr(TypeArr):
    """StrArr class for instance-checking."""
    _ref_type = str
    _size: ty.Optional[int] = None


class TypeArrFloat(TypeArr):
    """FloatArr class for instance-checking."""
    _ref_type = float
    _size: ty.Optional[int] = None


class ValueHolder(ty.Generic[KT]):
    """Simple value holder, can be transfered between variables."""

    def __init__(self, value: KT) -> None:
        self.__value: KT = value

    def set(self, value: KT) -> None:
        """Set value to holder."""
        self.__value = value

    def get(self) -> KT:
        """Get value from holder."""
        return self.__value


class VarParent(KspObject, HasInit, ty.Generic[KT], metaclass=VarMeta):
    """Base Generic class for every KSP object, recieves values.

    keeps self._ref_type, representing it's generic parent.
    generates init lines, if not declared as local."""
    names_count: int = 0
    _ref: ty.ClassVar[ty.Optional[ty.Type[KT]]] = None
    _ref_type: ty.Type[KT]

    class Persist:
        """Class for mark persistence of variable.

        can be:
        VarParent.not_persistent
        VarParent.persistent
        VarParent.inst_persistent
        VarParent.read_persistent"""

        def __init__(self, line: str = "") -> None:
            self.line = line

    not_persistent: ty.ClassVar[Persist] = Persist()
    persistent: ty.ClassVar[Persist] = Persist("make_persistent")
    inst_persistent: ty.ClassVar[Persist] = Persist("make_instr_persistent")
    read_persistent: ty.ClassVar[Persist] = Persist("make_persistent")

    def __init__(
            self,
            value: ty.Optional[KT] = None,
            name: str = "",
            persist: Persist = not_persistent,
            preserve_name: bool = False,
            *,
            local: bool = False,
    ) -> None:
        """Initialize.

        Value is Optional if instantiated within indexation[]
        name is strict if local=True
        persist can be optional if read() method called
        local only for internal library usage."""
        if local:
            if not name:
                raise TypeError("local name can not be empty")
            sup_name = NameBase(name)
            has_init = False
        else:
            if not name:
                name = f"VarParent{VarParent.names_count}"
                VarParent.names_count += 1
            sup_name = NameVar(name, preserve=preserve_name)
            has_init = True
        super().__init__(sup_name, has_init=has_init)
        if self._ref:
            self._ref_type: ty.Type[KT] = self._ref
        else:
            if value is None:
                raise TypeError('value or class subscription has to be used')
            self._ref_type = get_value_type(value)
        if value is None:
            value = self._ref_type()
        VarParent._ref = None
        self.name.prefix = self._get_type_prefix()
        self._persist: VarParent.Persist = persist
        self._array: ty.Optional[Arr[KT]] = None
        self._idx: ty.Optional[int] = None
        self._after_init(value)
        self._value: ValueHolder[KT]
        self._init_val: KT

    def _after_init(self, value: KT) -> None:
        """Co-initialization, if needed."""
        self._value: KT = ValueHolder(value)
        self._init_val: KT = value

    def _bound_to_array(self, array: 'Arr[KT]', idx: int) -> None:
        """Bound var to Arr cell."""
        if not issubclass(array._ref_type, self._ref_type):
            raise TypeError(f'Wrong array type: {array}')
        if not isinstance(idx, int):
            raise TypeError(f'idx can be only int, pasted {idx}')
        self._array = array
        self._idx = idx

    def _get_type_prefix(self) -> str:
        """Retrun correct prefix for self._ref_type."""
        if issubclass(self._ref_type, int):
            return "$"
        if issubclass(self._ref_type, str):
            return "@"
        if issubclass(self._ref_type, float):
            return "~"
        raise TypeError(f"Can't infer type of value")

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] with declaration line.

        for internal usage."""
        raise NotImplementedError

    def generate_init(self) -> ty.List[str]:
        """Return full initialization lines list."""
        out = self.get_decl_line()
        if self._persist is not self.not_persistent:
            out.append(f"{self._persist.line}({self.name()})")
        if self._persist is self.read_persistent:
            out.append(f"read_persistent_var({self.name()})")

        return out

    @property
    def val(self) -> KT:
        """Return RT value of Var or Arr."""
        if not self._array:
            return self._value.get()
        return self._array._value[ty.cast(int, self._idx)]

    @val.setter
    def val(self, val: KT) -> None:
        """Set RT value of Var or Arr.

        accepts only generics: int, str, float."""
        if not isinstance(val, self._ref_type):
            raise TypeError(
                'accepts only RT values of type {r}, pasted{v}'.format(
                    r=self._ref_type, v=val))
        if not self._array:
            self._value.set(val)
        else:
            self._array._value[ty.cast(int, self._idx)] = val

    def read(self) -> None:
        """Read persistent val in init cb.

        makes var persistent, if not."""
        if not self.in_init():
            raise RuntimeError('works only in init')
        if self._persist is VarParent.not_persistent:
            self._persist = self.persistent
        out = self.get_out()
        out.put_immediatly(AstString(f"read_persistent_var({self.name()})"))

    # @abstractmethod
    def __ilshift__(self: T, other: ATU) -> T:
        """Spetial abstract assignement operator."""
        raise NotImplementedError

    def copy(self: T, name: str, prefix: str, postfix: str) -> T:
        """Return new object of self type.

        For arr cells obj._array and obj._idx are loosed.
        init_val is loosed."""
        obj = self.__class__(  # type: ignore
            self.val, name=name, local=True)  # type: ignore
        obj.name.prefix = prefix  # type: ignore
        obj.name.postfix = postfix  # type: ignore
        return obj

    def _make_copy(self, other: ATU[KT], value: KT,
                   new_type: ty.Type[KVT]) -> KVT:
        """Return new Var[self._ref_type] object, depends on input val."""
        otpt = self.get_out()
        otpt.put_immediatly(AstAssign(self, other))
        if self.is_compiled():
            return self  # type: ignore
        name = self.name.name
        prefix = self.name.prefix
        postfix = self.name.postfix
        if isinstance(other, new_type):
            ret_obj = other.copy(name, prefix, postfix)  # type: ignore
            # ret_obj._init_val = other._init_val
        else:
            ret_obj = new_type(value, name, local=True)
            ret_obj.name.prefix = prefix
            ret_obj.name.postfix = postfix

        ret_obj._init_val = self._init_val
        ret_obj._array = self._array
        ret_obj._idx = self._idx
        ret_obj._value = self._value
        ret_obj.val = value

        return ret_obj

    @staticmethod
    def refresh() -> None:
        """Refresh Var autogenerated names."""
        VarParent.names_count = 0


VarRU = ty.Union["Num[int]", "Num[float]", "Str"]
VarIU = ty.Union[int, str, float]


class VarWrapperMeta(type):
    """Var getitem helper metaclass."""

    def __getitem__(cls, ref: ty.Type[VarIU]) -> ty.Type[VarRU]:
        """Return VarParent[ref] object."""
        VarParent._ref = ref  # type: ignore
        if issubclass(ref, (int, float)):
            return Num  # type: ignore
        if issubclass(ref, str):
            return Str

    def __instancecheck__(cls, instance: object) -> bool:
        return isinstance(instance, VarParent)


class Var(metaclass=VarWrapperMeta):
    def __new__(
            cls,
            value: VarIU,
            name: str = "",
            persist: VarParent.Persist = VarParent.not_persistent,
            preserve_name: bool = False,
            *,
            local: bool = False,
    ) -> VarRU:
        """Return new object of proper base concrete class."""
        if isinstance(value, int):
            return Num(
                value=value,
                name=name,
                persist=persist,
                preserve_name=preserve_name,
                local=local,
            )
        if isinstance(value, float):
            return Num(
                value=value,
                name=name,
                persist=persist,
                preserve_name=preserve_name,
                local=local,
            )
        if isinstance(value, str):
            return Str(
                value=value,
                name=name,
                persist=persist,
                preserve_name=preserve_name,
                local=local,
            )
        raise TypeError("can't infer type of value")


STT = (VarParent, str, ConcatsStrings)


class Str(VarParent[str], ConcatsStrings):
    """String KSP Var."""

    def __init__(
            self,
            value: str = "",
            name: str = "",
            persist: VarParent.Persist = VarParent.not_persistent,
            preserve_name: bool = False,
            *,
            local: bool = False,
    ) -> None:
        """Initialize.

        Value is Optional if instantiated within indexation[]
        name is strict if local=True
        persist can be optional if read() method called
        local only for internal library usage."""
        if not isinstance(value, str):
            raise TypeError(f"value has to be of str type. Pasted: {value}")
        VarParent._ref = str  # type: ignore
        super().__init__(
            value=value,
            name=name,
            persist=persist,
            preserve_name=preserve_name,
            local=local,
        )

    def __ilshift__(self, other: STU) -> "Str":
        """Return new Str object with name of self and value of other."""
        if not isinstance(other, STT):
            raise TypeError("incompatible type for assignement: " +
                            f"{type(other)} -> {STU}"  # type: ignore
                            )
        value = get_value(other)
        if not isinstance(value, str):
            value = f"{value}"
        ret_obj = self._make_copy(other, value, Str)

        return ret_obj

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] of simple declaration."""
        out = [f"declare {self.name()}"]
        if self._init_val:
            out.append(f'{self.name()} := "{self._init_val}"')
        return out

    def __iadd__(self, other: STU) -> "Str":  # type: ignore
        """Return new Str object, keep concatenated self+string."""
        return self.__ilshift__(AstConcatString(self, other))


class Num(VarParent[NT], ProcessNum[NT]):  # pylint: disable=R0901
    """Generic KSP numeric Var (int or float)."""

    def __init__(self,
                 value: ty.Optional[NT] = None,
                 name: str = "",
                 persist: VarParent.Persist = VarParent.not_persistent,
                 preserve_name: bool = False,
                 *,
                 local: bool = False) -> None:
        """Initialize.

        Value is Optional if instantiated within indexation[]
        name is strict if local=True
        persist can be optional if read() method called
        local only for internal library usage."""
        if VarParent._ref is None:
            if value is None:
                raise TypeError('has to be used value or class subsribtion')
            VarParent._ref = get_value_type(value)  # type: ignore
        super().__init__(  # type: ignore
            value=value,
            name=name,
            persist=persist,
            preserve_name=preserve_name,
            local=local,
        )

    def __ilshift__(self, other: ATU[NT]) -> "Num[NT]":  # type: ignore
        """Return new Num[self._ref_type] object.

        with name of self and value of other."""
        other = self._check_for_int(other)  # type: ignore
        value = get_value(other)
        if not isinstance(value, self._ref_type):
            raise TypeError(f"assigned to a value of wrong type: {value}")
        ret_obj = self._make_copy(other, value, Num)

        return ret_obj

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] of simple declaration."""
        value = ""
        if self._init_val:
            value = f" := {self._init_val}"
        out = [f"declare {self.name()}{value}"]
        return out

    @ducktype_num_magic
    def __iadd__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        return self.__ilshift__(AstAdd(self, other))

    @ducktype_num_magic
    def __isub__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        return self.__ilshift__(AstSub(self, other))

    @ducktype_num_magic
    def __imul__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        return self.__ilshift__(AstMul(self, other))

    @ducktype_num_magic
    def __itruediv__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        return self.__ilshift__(AstDiv(self, other))

    @ducktype_num_magic
    def __imod__(self, other: NTU[int]) -> "Num[int]":  # type: ignore
        if not issubclass(self._ref_type, int):
            raise TypeError("availble only for KSP int expression")
        return self.__ilshift__(AstMod(self, other))  # type: ignore

    @ducktype_num_magic
    def __ipow__(self, other: NTU[float]) -> "Num[float]":  # type: ignore
        if not issubclass(self._ref_type, float):
            raise TypeError("availble only for KSP float expression")
        return self.__ilshift__(AstPow(self, other))  # type: ignore

    def __iand__(self, other: NTU[NT]) -> ty.NoReturn:
        raise NotImplementedError

    def __ior__(self, other: NTU[NT]) -> ty.NoReturn:
        raise NotImplementedError

    def inc(self) -> None:
        """Increase value by 1, if int."""
        if not issubclass(self._ref_type, int):
            raise NotImplementedError
        inc(self)  # type: ignore

    def dec(self) -> None:
        """Decrease value by 1, if int."""
        if not issubclass(self._ref_type, int):
            raise NotImplementedError
        dec(self)  # type: ignore


def _assert_Num_int(var: NTU[int]) -> None:
    """Raise TypeError if not int or KspInt passed."""
    if not isinstance(var, Num):
        raise TypeError(f"can only be used with {Num[int]}")
    if not issubclass(get_value_type(var), int):
        raise TypeError(f"can only be used with {Num[int]}")


def inc(var: Num[int]) -> None:
    """Increase value by 1, if int."""
    _assert_Num_int(var)
    out = var.get_out()
    out.put_immediatly(AstBuiltInBase(None, "inc", var))
    var.val += 1


def dec(var: Num[int]) -> None:
    """Decrease value by 1, if int."""
    _assert_Num_int(var)
    out = var.get_out()
    out.put_immediatly(AstBuiltInBase(None, "dec", var))
    var.val -= 1


class AstAssign(AstRoot):
    """Root AST representing assignement."""

    def __init__(self, to_arg: "VarParent", from_arg: ATU) -> None:
        self.to_arg: "VarParent" = to_arg
        self.from_arg: ATU = from_arg

    def expand(self) -> str:
        """Return string representation of AST."""
        to = self.to_arg.name()
        from_str = get_compiled(self.from_arg)
        return f"{to} := {from_str}"

    def get_value(self) -> ty.NoReturn:
        """Raise AstBase.NullError."""
        raise self.NullError


class AstBuiltInBase(AstRoot, AstBase[KT]):
    """Root AST represents built-in KSP function."""
    _ref_type: ty.Optional[ty.Type[KT]]
    _value: ty.Optional[KT]
    args: ty.List[str]
    string: str

    def __init__(self, ret_val: ty.Optional[KT], string: str,
                 *args: ATU) -> None:
        if ret_val is not None:
            self._ref_type = get_value_type(ret_val)
        else:
            self._ref_type = None
        self._value: ty.Optional[KT] = ret_val
        self.args: ty.List[str] = list(map(get_compiled, args))
        self.string = string

    def expand(self) -> str:
        """Return string representation of AST."""
        return f'{self.string}({", ".join(self.args)})'

    def get_value(self) -> KT:
        """If ret_val, error is not raised."""
        if self._value is None:
            raise self.NullError
        return self._value


class AstOperatorUnary(AstBase[NT], ProcessNum[NT]):
    """Base class for AST numeric operator.

    arg parced
    string placed before arg
    priority conts in brackets placement."""

    arg1: NTU[NT]
    string: ty.ClassVar[str]
    priority: ty.ClassVar[int]

    def __init__(self, arg1: NTU[NT]) -> None:
        self._ref_type = get_value_type(arg1)
        self.arg1: NTU[NT] = arg1
        self.arg1_pure: NT = get_value(arg1)
        self.arg1_str: str = get_compiled(arg1)


class AstOperatorUnaryStandart(AstOperatorUnary[NT]):
    """Concrete simple unary operator AST."""

    def expand(self) -> str:
        """Return string+arg."""
        return f"{self.string}{self.arg1_str}"


class AstOperatorDouble(AstOperatorUnary[NT]):
    """Abstract base double operator AST."""
    arg2: NTU[NT]

    def __init__(self, arg1: NTU[NT], arg2: NTU[NT]) -> None:
        super().__init__(arg1)  # type: ignore
        self.arg2 = arg2
        self.arg2_pure: NT = get_value(arg2)
        self.arg2_str: str = get_compiled(arg2)


class AstOperatorDoubleStandart(AstOperatorDouble[NT]):
    """Concrete simple operator with 2 args.

    arg1 string arg2"""

    def _expand_with_string(self, string: str) -> str:
        pr: ty.List[int] = list()
        for arg in (self.arg1, self.arg2):
            if isinstance(arg, AstOperatorUnary):
                pr.append(arg.priority)
                continue
            pr.append(0)
        if self.priority <= pr[1]:
            self.arg2_str = f"({self.arg2_str})"
        if self.priority < pr[0]:
            self.arg1_str = f"({self.arg1_str})"
        return f"{self.arg1_str} {string} {self.arg2_str}"

    def expand(self) -> str:
        """Return arg1 str arg2, with placing brackets."""
        return self._expand_with_string(self.string)


class AstOperatorUnaryBracket(AstOperatorUnary[NT]):
    """Conctere bracket unary operator AST.

    string(arg1)"""

    def expand(self) -> str:
        """Return string(arg1)."""
        return f"{self.string}({self.arg1_str})"


class AstOperatorDoubleBracket(AstOperatorDouble[NT]):
    """Conctere bracket double operator AST.

    string(arg1, arg2)"""

    def expand(self) -> str:
        """Return string(arg1, arg2)."""
        return f"{self.string}({self.arg1_str}, {self.arg2_str})"


class AstBool(AstBase[NT]):
    """Spetial AST operator, hasn't got get_value method.

    has expand_bool and bool(AstBool()) instead."""

    @abstractmethod
    def __bool__(self) -> bool:
        """Return bolean value of AST."""

    def expand_bool(self) -> str:
        """Return "bool string" representation."""
        return self.expand()


def _check_if_bool(arg: NTU[NT]) -> ty.Union[NT, bool]:
    if isinstance(arg, AstBool):
        return arg is True
    return get_value(arg)


class AstCanBeBool(AstOperatorDoubleStandart[NT], AstBool[NT]):
    """Combines Standart double and bool AST operators."""
    string_bool: ty.ClassVar[str]
    arg1_pure: ty.Union[NT, bool]  # type: ignore
    arg2_pure: ty.Union[NT, bool]  # type: ignore

    def __init__(
            self,
            arg1: NTU[NT],  # pylint: disable=W0231
            arg2: NTU[NT]) -> None:  # pylint: disable=W0231
        """Calculate as bitwise as bool values and strings."""
        if isinstance(arg1, AstBool):
            self._ref_type = bool
        else:
            self._ref_type = get_value_type(arg1)
        self.arg1 = arg1
        self.arg1_pure = _check_if_bool(arg1)
        if isinstance(arg1, AstCanBeBool):
            self.arg1_str: str = arg1.expand_bool()
        else:
            self.arg1_str = get_compiled(arg1)
        self.arg2 = arg2
        self.arg2_pure: NT = _check_if_bool(arg2)
        if isinstance(arg2, AstCanBeBool):
            self.arg2_str: str = arg2.expand_bool()
        else:
            self.arg2_str = get_compiled(arg2)

    def expand(self) -> str:
        """Return bitwise str repr, or bool, if in boolean context."""
        if self.is_bool():
            return self.expand_bool()
        return super().expand()

    def expand_bool(self) -> str:
        """Return bolean string repr of self and contained ASTs."""
        return self._expand_with_string(self.string_bool)


class AstNeg(AstOperatorUnaryStandart[NT]):
    """Negative AST operator."""
    priority = 2
    string = "-"

    def get_value(self) -> NT:
        """Return -agr."""
        return -self.arg1_pure


class AstNot(AstOperatorUnaryStandart[int]):
    """Bitwise not AST operator.

    works only for ints."""
    priority = 2
    string = ".not."

    def get_value(self) -> int:
        if not issubclass(self._ref_type, int):
            raise TypeError("works only on ints")
        return ~self.arg1_pure


class AstAbs(AstOperatorUnaryBracket[NT]):
    """Absolute val operator."""
    priority = 2
    string = "abs"

    def get_value(self) -> NT:
        return abs(self.arg1_pure)


class AstInt(AstOperatorUnaryBracket[int]):
    """Represent KSP real_to_int function."""
    priority = 2
    string = "real_to_int"
    arg1: NTU[float]  # type: ignore
    arg1_pure: int
    arg1_str: str

    def __init__(self, arg1: NTU[float]) -> None:  # pylint: disable=W0231
        self._ref_type = int
        self.arg1: NTU[float] = arg1
        self.arg1_pure: int = int(get_value(arg1))
        self.arg1_str: str = get_compiled(arg1)

    def get_value(self) -> int:
        """Return int(arg)."""
        return int(self.arg1_pure)


class AstFloat(AstOperatorUnaryBracket[float]):
    """Represent KSP int_to_real function."""
    priority = 2
    string = "int_to_real"
    arg1: NTU[int]  # type: ignore
    arg1_pure: float
    arg1_str: str

    def __init__(self, arg1: NTU[int]) -> None:  # pylint: disable=W0231
        self._ref_type = float
        self.arg1: NTU[int] = arg1
        self.arg1_pure: float = float(get_value(arg1))
        self.arg1_str: str = get_compiled(arg1)

    def get_value(self) -> float:
        """Return float(arg)."""
        return float(self.arg1_pure)


class AstAdd(AstOperatorDoubleStandart[NT]):
    """Addition AST stanfart double operator."""
    priority = 4
    string = "+"

    def get_value(self) -> NT:
        return self.arg1_pure + self.arg2_pure


class AstSub(AstOperatorDoubleStandart[NT]):
    """Substitution AST stanfart double operator."""
    priority = 4
    string = "-"

    def get_value(self) -> NT:
        return self.arg1_pure - self.arg2_pure


class AstDiv(AstOperatorDoubleStandart[NT]):
    """Division AST stanfart double operator."""
    priority = 3
    string = "/"

    def get_value(self) -> NT:
        try:
            if isinstance(self.arg1_pure, int):
                return self.arg1_pure // self.arg2_pure
            return self.arg1_pure / self.arg2_pure
        except ZeroDivisionError:
            if isinstance(self.arg1_pure, int):
                return 0
            return 0.0


class AstMul(AstOperatorDoubleStandart[NT]):
    """Multiplication AST stanfart double operator."""
    priority = 3
    string = "*"

    def get_value(self) -> NT:
        return self.arg1_pure * self.arg2_pure


class AstMod(AstOperatorDoubleStandart[int]):
    """Modulo (int) AST stanfart double operator."""
    priority = 3
    string = "mod"

    def get_value(self) -> int:
        return self.arg1_pure % self.arg2_pure


class AstPow(AstOperatorDoubleBracket[float]):
    """Power (float) AST stanfart double operator."""
    priority = 1
    string = "pow"

    def get_value(self) -> float:
        return self.arg1_pure**self.arg2_pure


class AstLshift(AstOperatorDoubleBracket[int]):
    """Bitwise shift left AST bracket double operator."""
    priority = 5
    string = "sh_left"

    def get_value(self) -> int:
        return self.arg1_pure << self.arg2_pure


class AstRshift(AstOperatorDoubleBracket[int]):
    """Bitwise shift right AST bracket double operator."""
    priority = 5
    string = "sh_right"

    def get_value(self) -> int:
        return self.arg1_pure >> self.arg2_pure


class AstAnd(AstCanBeBool[NT]):
    """Bitwise and logical and AST CanBeBool operator."""
    priority = 7
    string = ".and."
    string_bool = "and"

    def get_value(self) -> NT:
        if not issubclass(self._ref_type, int):
            raise TypeError("waorks only on ints")
        return self.arg1_pure & self.arg2_pure  # type: ignore

    def __bool__(self) -> bool:
        if self.arg1 and self.arg2:
            return True
        return False


class AstOr(AstCanBeBool[NT]):
    """Bitwise or logical and AST CanBeBool operator."""
    priority = 8
    string = ".or."
    string_bool = "or"

    def get_value(self) -> NT:
        if not issubclass(self._ref_type, int):
            raise TypeError("waorks only on ints")
        return self.arg1_pure | self.arg2_pure  # type: ignore

    def __bool__(self) -> bool:
        if self.arg1 or self.arg2:
            return True
        return False


class OperatorComparisson(AstOperatorDoubleStandart[NT], AstBool[NT]):
    """Base class for "just boolean" AST operators."""

    def expand(self) -> str:
        """Set context to bool with invocation."""
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


class AstEq(OperatorComparisson[NT]):  # pylint: disable=W0223
    """Equals AST Bool operator."""
    priority = 6
    string = "="

    def __bool__(self) -> bool:
        if self.arg1_pure == self.arg2_pure:
            return True
        return False


class AstNe(OperatorComparisson[NT]):  # pylint: disable=W0223
    """Not equals AST Bool operator."""
    priority = 6
    string = "#"

    def __bool__(self) -> bool:
        if self.arg1_pure != self.arg2_pure:
            return True
        return False


class AstLt(OperatorComparisson[NT]):  # pylint: disable=W0223
    """Less than AST Bool operator."""
    priority = 6
    string = "<"

    def __bool__(self) -> bool:
        if self.arg1_pure < self.arg2_pure:
            return True
        return False


class AstGt(OperatorComparisson[NT]):  # pylint: disable=W0223
    """Greater than AST Bool operator."""
    priority = 6
    string = ">"

    def __bool__(self) -> bool:
        if self.arg1_pure > self.arg2_pure:
            return True
        return False


class AstLe(OperatorComparisson[NT]):  # pylint: disable=W0223
    """Less or equal AST Bool operator."""
    priority = 6
    string = "<="

    def __bool__(self) -> bool:
        if self.arg1_pure <= self.arg2_pure:
            return True
        return False


class AstGe(OperatorComparisson[NT]):  # pylint: disable=W0223
    """Greater or equal AST Bool operator."""
    priority = 6
    string = ">="

    def __bool__(self) -> bool:
        if self.arg1_pure >= self.arg2_pure:
            return True
        return False


def infer_arr_ref(
        value: ty.Optional[ty.Union[KT, ty.List[KT]]]) -> ty.Type[KT]:
    if VarParent._ref:
        if value:
            if isinstance(value, ty.List):
                _value = value[0]
            else:
                _value = value
            if not isinstance(_value, VarParent._ref):
                raise TypeError(f'value {value} not of type {VarParent._ref}')
        return VarParent._ref  # type: ignore
    if not value:
        raise TypeError('value or class subscription has to be used')
    if isinstance(value, ty.List):
        return get_value_type(value[0])
    return get_value_type(value)


class Arr(VarParent, ty.Generic[KT]):
    """Generic KSP array class.

    * value can be as list of generic, as well as generic itself
        e.g. declare array[size] := (val)
    * name can be optional if array is not local
    * size is optional, but it helps to keep self in broads"""

    _value: ty.List[KT]  # type: ignore
    _vars: ty.List[ty.Optional[VarParent[KT]]]

    def __init__(  # pylint: disable=R0913
            self,
            value: ty.Optional[ty.Union[KT, ty.List[KT]]] = None,
            name: str = "",
            persist: VarParent.Persist = VarParent.not_persistent,
            preserve_name: bool = False,
            size: ty.Optional[int] = None,
            *,
            local: bool = False,
    ) -> None:
        """Represent all three types of KSP arrays.

        * value can be as list of generic, as well as generic itself
            e.g. declare array[size] := (val)
        * name can be optional if array is not local
        * size is optional, but it helps to keep self in broads"""
        self._ref_type = infer_arr_ref(value)
        if issubclass(self._ref_type,
                      str) and persist is not VarParent.not_persistent:
            raise RuntimeError('String array can not be persistent')
        if not value:
            value = self._ref_type()
        value = ty.cast(ty.Union[KT, ty.List[KT]], value)
        self._init_size = size
        self._size = 0
        if not isinstance(value, ty.List):
            if not value:
                self._size = 0
            else:
                self._size = 1
            self._init_seq: ty.List[KT] = [value]
            _size = size
            if size is None:
                _size = 1
            _value = [value] * ty.cast(int, _size)
            self._default: KT = value
        else:
            self._default = self._ref_type()
            self._size = len(value)
            self._init_seq = value.copy()
            _value = value
            value = value[0]
        super().__init__(
            value=value,
            name=name,
            persist=persist,
            preserve_name=preserve_name,
            local=local,
        )
        self._value = _value
        self._vars = [None] * len(_value)
        self._recieved_rt: bool = False

    def read(self) -> None:
        """Read persistent val in init cb.

        makes var persistent, if not."""
        if issubclass(self._ref_type, str):
            raise RuntimeError('String array can not be persistent')
        super().read()

    def _after_init(self, value: ty.List[KT]) -> None:
        return

    def _resolve_idx(self, idx: NTU[int]) -> ty.Tuple[str, int]:
        """Return tuple of str(idx) and RT(idx)."""
        c_idx = get_compiled(idx)
        r_idx = get_value(idx)
        if not isinstance(r_idx, int):
            raise IndexError(f"index has to be resolved to int, pasted: {idx}")
        if r_idx < 0:
            r_idx = self.__len__() - abs(r_idx)
            c_idx = get_compiled(self.__len__() - abs(idx))  # type: ignore
        return c_idx, r_idx

    def __getitem__(self, idx: NTU[int]) -> VarParent[KT]:
        """Return Var[self._ref_type] instance, bounded to the cell at idx."""
        c_idx, r_idx = self._resolve_idx(idx)
        return self._get_cashed_item(c_idx, r_idx)

    def __setitem__(self, idx: NTU[int], value: VarParent[KT]) -> None:
        """Assign bounded var to array cell."""
        if not isinstance(value, Type[self._ref_type]):
            raise TypeError("has to be of type {T}[{r}], pasted: {v}".format(
                T=VarParent, r=self._ref_type, v=value))
        if value._array is not self:
            raise RuntimeError("use <<= operator")
        c_idx, r_idx = self._resolve_idx(idx)  # pylint: disable=W0612
        self._vars[r_idx] = value

    def _get_cashed_item(self, c_idx: str, r_idx: int) -> VarParent[KT]:
        """Return cashed var from cell with modified str idx.

        or cash (instantiate) one."""
        obj: VarParent[KT]
        if isinstance(self._vars[r_idx], VarParent):
            obj = self._vars[r_idx]  # type: ignore
        else:
            self._vars[r_idx] = Var[self._ref_type](  # type: ignore
                self._value[r_idx],
                self.name.name,
                local=True)
            obj = self._vars[r_idx]  # type: ignore
        obj.name.postfix = f"[{c_idx}]"
        obj.name.prefix = self.name.prefix
        obj._bound_to_array(self, r_idx)
        return obj

    def _get_type_prefix(self) -> str:
        """Arr representation of the same Var method."""
        if issubclass(self._ref_type, int):
            return "%"
        if issubclass(self._ref_type, str):
            return "!"
        if issubclass(self._ref_type, float):
            return "?"
        raise TypeError("can't infer type")

    def _gen_decl_seq_item(self, idx: int, i: KT) -> str:
        """Decl_line halper function."""
        if i is None:
            return str(self._ref_type())
        if not isinstance(i, self._ref_type):
            raise TypeError(f"value ({i}) at idx {idx} of a wrong type: {i}")
        return str(i)

    def get_decl_line(self) -> ty.List[str]:
        """Return declaration line with as much inlined values as possible."""
        if issubclass(self._ref_type, str):
            return self._get_decl_line_str()
        return self._get_decl_line_num()

    def _get_decl_line_str(self) -> ty.List[str]:
        """Return multi-item list with assignements to array."""
        out = [f"declare {self.name()}[{self._size}]"]
        for idx, i in enumerate(self._init_seq):
            if not isinstance(i, str):
                raise TypeError(f'value {i} at idx {idx} is not of type str')
            out.append(f'{self.name()}[{idx}] := "{i}"')
        return out

    def _get_decl_line_num(self) -> ty.List[str]:
        """Return long declaration string in one-item list."""
        value = ""

        if len(self._init_seq) != 1 or self._init_seq[0]:
            value = ", ".join([
                self._gen_decl_seq_item(idx, i)
                for idx, i in enumerate(self._init_seq)
            ])
        if value:
            value = f" := ({value})"
        return [f"declare {self.name()}[{self._size}]{value}"]

    def __ilshift__(self, other: ATU[KT]) -> ty.NoReturn:
        """Raise NotImplementedError."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Return current RT length of array."""
        return len(self._value)

    def _append_is_possible(self) -> bool:
        """Check if append is possible.

        Raises RuntimeError"""
        if not self.in_init():
            raise RuntimeError("can append only outside callbacks")
        if not self._init_size or self._size < self._init_size:
            return True
        raise RuntimeError("can't append, Array is full")

    def append(self, value: ATU[KT]) -> None:
        """Append value to array, if it is still init cb."""
        self._append_is_possible()
        if not isinstance(get_value(value), self._ref_type):
            raise TypeError(
                "pasted value of wront type: {v}, expected {r}".format(
                    v=value, r=self._ref_type))
        if isinstance(value, Type[self._ref_type]):
            self._recieved_rt = True
        _value = get_value(value)
        try:
            self._value[self._size] = _value
        except IndexError:
            self._value.append(_value)
            self._vars.append(None)
        if not self._recieved_rt:
            self._init_seq.append(value)  # type: ignore
        else:
            self[self._size] <<= value
        self._size += 1

    @property
    def val(self) -> ty.List[KT]:
        """Return RT value of Var or Arr."""
        return self._value

    @val.setter
    def val(self, val: KT) -> None:
        """Set RT value of Var or Arr.

        accepts only generics: int, str, float."""
        if not isinstance(val, ty.List) or not isinstance(
                val[0], self._ref_type):
            raise TypeError(
                'accepts only RT values of type List[int], pasted{v}'.format(
                    r=self._ref_type, v=val))
        self._value = val

    def __iter__(self) -> ty.NoReturn:
        raise NotImplementedError('for maintainable iteration use For class')
