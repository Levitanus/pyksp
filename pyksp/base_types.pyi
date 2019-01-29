"""Base KSP types and compiler mechanics."""
import typing as ty
from abc import abstractmethod

from .abstract import KspObject
from .abstract import AstRoot
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
NTU = ty.Union["VarParent[NT]", "AstBase[NT]", "ProcessNum[NT]", NT]
NotVarNTU = ty.Union["AstBase[NT]", "ProcessNum[NT]", NT]


@ty.overload
def get_value(value: ATU[int]) -> int:
    """Retrieve realtime value of object."""
    ...


@ty.overload
def get_value(value: ATU[str]) -> str:
    """Retrieve realtime value of object."""
    ...


@ty.overload
def get_value(value: ATU[float]) -> float:
    """Retrieve realtime value of object."""
    ...


@ty.overload
def get_compiled(value: ATU[int]) -> str:
    """Retrive KSP representation of object."""
    ...


@ty.overload
def get_compiled(value: ATU[str]) -> str:
    """Retrive KSP representation of object."""
    ...


@ty.overload
def get_compiled(value: ATU[float]) -> str:
    """Retrive KSP representation of object."""
    ...


def get_value_type(value: ATU[KT]) -> ty.Type[KT]:
    """Retrive generic reference type of object."""
    ...


class Magic(KSP, ty.Generic[KT]):
    """Base class for types with magic methods."""
    ...


class ConcatsStrings(Magic[str]):
    """Supports str, ConcatStr and any Var objects concatenation."""

    def __add__(self, other: STU) -> "AstConcatString":
        """Return AstConcatString object."""
        ...

    def __radd__(self, other: STU) -> "AstConcatString":
        """Return AstConcatString object."""
        ...


class AstConcatString(AstBase[str], ConcatsStrings):
    """Ast, handles strings concatenation."""

    _ref_type: str
    arg1: STU
    arg2: STU

    def __init__(self, arg1: STU, arg2: STU) -> None:
        """Accept args and initialize ref_type."""
        ...

    def expand(self) -> str:
        """Return KSP string representation."""
        ...

    def get_value(self) -> str:
        """Return concatenated string."""
        ...

    def __iadd__(self, other: STU) -> ty.NoReturn:
        """Not implemented."""
        ...


FT = ty.TypeVar("FT", bound=ty.Callable[..., ty.Any])


def ducktype_num_magic(method: FT) -> FT:
    """Check that ref_type of other is campatible with self."""
    ...


class ProcessNum(Magic[NT], ty.Generic[NT]):
    """Base class for objects, keeps int and float values."""

    _ref_type: ty.Type[NT]

    def _check_for_int(self, other: NTU[NT]) -> ty.Union[NTU[NT], float]:
        """Convert int to float if self._ref_type is float."""
        ...

    def __neg__(self) -> "AstNeg[NT]":
        """Return AstNeg object."""
        ...

    def __invert__(self) -> "AstNot":
        """Return AstNot object if self ref is int."""
        ...

    @ducktype_num_magic
    def __add__(self, other: NTU[NT]) -> "AstAdd[NT]":
        """Return AstAdd[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __radd__(self, other: NTU[NT]) -> "AstAdd[NT]":
        """Return AstAdd[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __sub__(self, other: NTU[NT]) -> "AstSub[NT]":
        """Return AstSub[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __rsub__(self, other: NTU[NT]) -> "AstSub[NT]":
        """Return AstSub[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __mul__(self, other: NTU[NT]) -> "AstMul[NT]":
        """Return AstMul[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __rmul__(self, other: NTU[NT]) -> "AstMul[NT]":
        """Return AstMul[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __truediv__(self, other: NTU[NT]) -> "AstDiv[NT]":
        """Return AstDiv[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __rtruediv__(self, other: NTU[NT]) -> "AstDiv[NT]":
        """Return AstDiv[self._ref_type] object."""
        ...

    def __mod__(self, other: NTU[int]) -> "AstMod":
        """Return AstMod object if self._ref_type is int."""
        ...

    def __rmod__(self, other: NTU[int]) -> "AstMod":
        """Return AstMod object if self._ref_type is int."""
        ...

    def __pow__(self, other: NTU[float]) -> "AstPow":
        """Return AstPow object if self._ref_type is float."""
        ...

    def __rpow__(self, other: NTU[float]) -> "AstPow":
        """Return AstPow object if self._ref_type is float."""
        ...

    def __and__(self, other: NTU[NT]) -> "AstAnd[NT]":
        """Return AstAnd[self._ref_type] object."""
        ...

    def __rand__(self, other: NTU[NT]) -> "AstAnd[NT]":
        """Return AstAnd[self._ref_type] object."""
        ...

    def __or__(self, other: NTU[NT]) -> "AstOr[NT]":
        """Return AstOr[self._ref_type] object."""
        ...

    def __ror__(self, other: NTU[NT]) -> "AstOr[NT]":
        """Return AstOr[self._ref_type] object."""
        ...

    @ducktype_num_magic
    def __eq__(self, other: NTU[NT]) -> "AstEq[NT]":  # type: ignore
        """Return AstEq object.

        note: AstEq is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstEq)"""
        ...

    @ducktype_num_magic
    def __ne__(self, other: NTU[NT]) -> "AstNe[NT]":  # type: ignore
        """Return AstNe object.

        note: AstNe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstNe)"""
        ...

    @ducktype_num_magic
    def __lt__(self, other: NTU[NT]) -> "AstLt[NT]":
        """Return AstLt object.

        note: AstLt is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstLt)"""
        ...

    @ducktype_num_magic
    def __gt__(self, other: NTU[NT]) -> "AstGt[NT]":
        """Return AstGt object.

        note: AstGt is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstGt)"""
        ...

    @ducktype_num_magic
    def __le__(self, other: NTU[NT]) -> "AstLe[NT]":
        """Return AstLe object.

        note: AstLe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstLe)"""
        ...

    @ducktype_num_magic
    def __ge__(self, other: NTU[NT]) -> "AstGe[NT]":
        """Return AstGe object.

        note: AstGe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstGe)"""
        ...

    def __abs__(self) -> "AstAbs[NT]":
        """Return AstAbs[self._ref_type] object."""
        return AstAbs(self)

    def to_int(self) -> "AstInt":
        """Return AstInt object if self._ref_type is float."""
        ...

    def to_float(self) -> "AstFloat":
        """Return AstFloat object if self._ref_type is int."""
        ...

    def __lshift__(self, other: NTU[int]) -> "AstLshift":
        """Return AstLshift object if self._ref_type is int."""
        ...

    def __rlshift__(self, other: NTU[int]) -> "AstLshift":
        """Return AstLshift object if self._ref_type is int."""
        ...

    def __rshift__(self, other: NTU[int]) -> "AstRshift":
        """Return AstRshift object if self._ref_type is int."""
        ...

    def __rrshift__(self, other: NTU[int]) -> "AstRshift":
        """Return AstRshift object if self._ref_type is int."""
        ...


def to_int(value: ProcessNum) -> "AstInt":
    """Return AstInt object if value._ref_type is float."""
    ...


def to_float(value: ProcessNum) -> "AstFloat":
    """Return AstFloat object if value._ref_type is int."""
    ...


class VarMeta(KSPBaseMeta):
    """Big Scary metaclass.

    combines Generic nature within RT duck_typing.
    if Var was initialized within [type] indexing, ref_type inferred by it.
    Otherwise by init value."""

    def __getitem__(cls, *args: ty.Type[KT],
                    **kwargs: ty.Any) -> ty.Type["VarParent[KT]"]:
        """The next class initialization will be infered as passed type."""
        ...


class TypeMeta(type):
    """Metaclass for simplifying instance-check."""

    def __instancecheck__(cls, instance: "VarParent") -> bool:
        ...

    def __getitem__(
            cls,
            ref: ty.Union[ty.Type[KT], ty.Tuple[ty.Type[KT], ty.
                                                Union[int, bool]]],
    ) -> ty.Type["Type"]:
        ...


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
        ...

    def set(self, value: KT) -> None:
        """Set value to holder."""
        ...

    def get(self) -> KT:
        """Get value from holder."""
        ...


class VarParent(KspObject, HasInit, ty.Generic[KT], metaclass=VarMeta):
    """Base Generic class for every KSP object, recieves values.

    keeps self._ref_type, representing it's generic parent.
    generates init lines, if not declared as local."""
    names_count: int = 0
    _ref: ty.ClassVar[ty.Optional[ty.Type[KT]]]
    _ref_type: ty.Type[KT]
    _persist: 'VarParent'.Persist
    _array: ty.Optional['Arr' [KT]]
    _idx: ty.Optional[int]
    _value: ValueHolder[KT]
    _init_val: KT

    class Persist:
        """Class for mark persistence of variable.

        can be:
        VarParent.not_persistent
        VarParent.persistent
        VarParent.inst_persistent
        VarParent.read_persistent"""

        line: str

        def __init__(self, line: str = "") -> None:
            ...

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
        ...

    def _after_init(self, value: KT) -> None:
        """Co-initialization, if needed."""
        ...

    def _bound_to_array(self, array: 'Arr[KT]', idx: int) -> None:
        """Bound var to Arr cell."""
        ...

    def _get_type_prefix(self) -> str:
        """Retrun correct prefix for self._ref_type."""
        ...

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] with declaration line.

        for internal usage."""
        ...

    def generate_init(self) -> ty.List[str]:
        """Return full initialization lines list."""
        ...

    @property
    def val(self) -> KT:
        """Return RT value of Var or Arr."""
        ...

    @val.setter
    def val(self, val: KT) -> None:
        """Set RT value of Var or Arr.

        accepts only generics: int, str, float."""
        ...

    def read(self) -> None:
        """Read persistent val in init cb.

        makes var persistent, if not."""
        ...

    def __ilshift__(self: T, other: ATU) -> T:
        """Spetial abstract assignement operator."""
        ...

    def copy(self: T, name: str, prefix: str, postfix: str) -> T:
        """Return new object of self type.

        For arr cells obj._array and obj._idx are loosed.
        init_val is loosed."""
        ...

    def _make_copy(self, other: ATU[KT], value: KT,
                   new_type: ty.Type[KVT]) -> KVT:
        """Return new Var[self._ref_type] object, depends on input val."""
        ...

    @staticmethod
    def refresh() -> None:
        """Refresh Var autogenerated names."""
        ...


VarRU = ty.Union["Num[int]", "Num[float]", "Str"]
VarIU = ty.Union[int, str, float]


class VarWrapperMeta(type):
    """Var getitem helper metaclass."""

    @ty.overload
    def __getitem__(cls, ref: ty.Type[int]) -> ty.Type["Num[int]"]:
        ...

    @ty.overload
    def __getitem__(cls, ref: ty.Type[float]) -> ty.Type["Num[float]"]:
        ...

    @ty.overload
    def __getitem__(cls, ref: ty.Type[str]) -> ty.Type["Str"]:
        ...

    def __instancecheck__(cls, instance: object) -> bool:
        ...


class Var(metaclass=VarWrapperMeta):
    @ty.overload
    def __new__(
            cls,
            value: str,
            name: str = "",
            persist: VarParent.Persist = VarParent.not_persistent,
            preserve_name: bool = False,
            *,
            local: bool = False,
    ) -> 'Str':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
            cls,
            value: int,
            name: str = "",
            persist: VarParent.Persist = VarParent.not_persistent,
            preserve_name: bool = False,
            *,
            local: bool = False,
    ) -> 'Num[int]':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
            cls,
            value: float,
            name: str = "",
            persist: VarParent.Persist = VarParent.not_persistent,
            preserve_name: bool = False,
            *,
            local: bool = False,
    ) -> 'Num[float]':
        """Return new object of proper base concrete class."""
        ...


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
        ...

    def __ilshift__(self, other: STU) -> "Str":
        """Return new Str object with name of self and value of other."""
        ...

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] of simple declaration."""
        ...

    def __iadd__(self, other: STU) -> "Str":  # type: ignore
        """Return new Str object, keep concatenated self+string."""
        ...


class Num(VarParent[NT], ProcessNum[NT]):
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
        ...

    def __ilshift__(self, other: ATU[NT]) -> "Num[NT]":  # type: ignore
        """Return new Num[self._ref_type] object.

        with name of self and value of other."""
        ...

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] of simple declaration."""
        ...

    @ducktype_num_magic
    def __iadd__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        ...

    @ducktype_num_magic
    def __isub__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        ...

    @ducktype_num_magic
    def __imul__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        ...

    @ducktype_num_magic
    def __itruediv__(self, other: NTU[NT]) -> "Num[NT]":  # type: ignore
        ...

    @ducktype_num_magic
    def __imod__(self, other: NTU[int]) -> "Num[int]":  # type: ignore
        ...

    @ducktype_num_magic
    def __ipow__(self, other: NTU[float]) -> "Num[float]":  # type: ignore
        ...

    def __iand__(self, other: NTU[NT]) -> ty.NoReturn:
        ...

    def __ior__(self, other: NTU[NT]) -> ty.NoReturn:
        ...

    def inc(self) -> None:
        """Increase value by 1, if int."""
        ...

    def dec(self) -> None:
        """Decrease value by 1, if int."""
        ...


def _assert_Num_int(var: NTU[int]) -> None:
    """Raise TypeError if not int or KspInt passed."""
    ...


def inc(var: Num[int]) -> None:
    """Increase value by 1, if int."""
    ...


def dec(var: Num[int]) -> None:
    """Decrease value by 1, if int."""
    ...


class AstAssign(AstRoot):
    """Root AST representing assignement."""

    to_arg: "VarParent"
    from_arg: ATU

    def __init__(self, to_arg: "VarParent", from_arg: ATU) -> None:
        ...

    def expand(self) -> str:
        """Return string representation of AST."""
        ...

    def get_value(self) -> ty.NoReturn:
        """Raise AstBase.NullError."""
        ...


class AstBuiltInBase(AstRoot, AstBase[KT]):
    """Root AST represents built-in KSP function."""
    _ref_type: ty.Optional[ty.Type[KT]]
    _value: ty.Optional[KT]
    args: ty.List[str]
    string: str

    def __init__(self, ret_val: ty.Optional[KT], string: str,
                 *args: ATU) -> None:
        ...

    def expand(self) -> str:
        """Return string representation of AST."""
        ...

    def get_value(self) -> KT:
        """If ret_val, error is not raised."""
        ...


class AstOperatorUnary(AstBase[NT], ProcessNum[NT]):  # type: ignore
    """Base class for AST numeric operator.

    arg parced
    string placed before arg
    priority conts in brackets placement."""

    arg1: NTU[NT]
    string: ty.ClassVar[str]
    priority: ty.ClassVar[int]
    _ref_type: ty.Type[NT]
    arg1_pure: NT
    arg1_str: str

    def __init__(self, arg1: NTU[NT]) -> None:
        ...


class AstOperatorUnaryStandart(AstOperatorUnary[NT]):  # type: ignore
    """Concrete simple unary operator AST."""

    def expand(self) -> str:
        """Return string+arg."""
        ...


class AstOperatorDouble(AstOperatorUnary[NT]):  # type: ignore
    """Abstract base double operator AST."""
    arg2: NTU[NT]
    arg2_pure: NT
    arg2_str: str

    def __init__(self, arg1: NTU[NT], arg2: NTU[NT]) -> None:
        ...


class AstOperatorDoubleStandart(AstOperatorDouble[NT]):  # type: ignore
    """Concrete simple operator with 2 args.

    arg1 string arg2"""

    def _expand_with_string(self, string: str) -> str:
        ...

    def expand(self) -> str:
        """Return arg1 str arg2, with placing brackets."""
        ...


class AstOperatorUnaryBracket(AstOperatorUnary[NT]):  # type: ignore
    """Conctere bracket unary operator AST.

    string(arg1)"""

    def expand(self) -> str:
        """Return string(arg1)."""
        ...


class AstOperatorDoubleBracket(AstOperatorDouble[NT]):  # type: ignore
    """Conctere bracket double operator AST.

    string(arg1, arg2)"""

    def expand(self) -> str:
        """Return string(arg1, arg2)."""
        ...


class AstBool(AstBase[NT]):
    """Spetial AST operator, hasn't got get_value method.

    has expand_bool and bool(AstBool()) instead."""

    @abstractmethod
    def __bool__(self) -> bool:
        """Return bolean value of AST."""
        ...

    def expand_bool(self) -> str:
        """Return "bool string" representation."""
        ...


def _check_if_bool(arg: NTU[NT]) -> ty.Union[NT, bool]:
    ...


class AstCanBeBool(AstOperatorDoubleStandart[NT], AstBool[NT]):  # type: ignore
    """Combines Standart double and bool AST operators."""
    string_bool: ty.ClassVar[str]
    arg1_pure: ty.Union[NT, bool]  # type: ignore
    arg2_pure: ty.Union[NT, bool]  # type: ignore

    def __init__(self, arg1: NTU[NT], arg2: NTU[NT]) -> None:
        """Calculate as bitwise as bool values and strings."""
        ...

    def expand(self) -> str:
        """Return bitwise str repr, or bool, if in boolean context."""
        ...

    def expand_bool(self) -> str:
        """Return bolean string repr of self and contained ASTs."""
        ...


class AstNeg(AstOperatorUnaryStandart[NT]):
    """Negative AST operator."""
    string = "-"

    def get_value(self) -> NT:
        """Return -agr."""
        ...


class AstNot(AstOperatorUnaryStandart[int]):
    """Bitwise not AST operator.

    works only for ints."""

    def get_value(self) -> int:
        ...


class AstAbs(AstOperatorUnaryBracket[NT]):
    """Absolute val operator."""

    def get_value(self) -> NT:
        ...


class AstInt(AstOperatorUnaryBracket[int]):
    """Represent KSP real_to_int function."""
    priority = 2
    string = "real_to_int"
    arg1: NTU[float]  # type: ignore
    arg1_pure: int
    arg1_str: str

    def __init__(self, arg1: NTU[float]) -> None:
        ...

    def get_value(self) -> int:
        """Return int(arg)."""
        ...


class AstFloat(AstOperatorUnaryBracket[float]):
    """Represent KSP int_to_real function."""
    arg1: NTU[int]  # type: ignore
    arg1_pure: float
    arg1_str: str

    def __init__(self, arg1: NTU[int]) -> None:
        ...

    def get_value(self) -> float:
        """Return float(arg)."""
        ...


class AstAdd(AstOperatorDoubleStandart[NT]):
    """Addition AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstSub(AstOperatorDoubleStandart[NT]):
    """Substitution AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstDiv(AstOperatorDoubleStandart[NT]):
    """Division AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstMul(AstOperatorDoubleStandart[NT]):
    """Multiplication AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstMod(AstOperatorDoubleStandart[int]):
    """Modulo (int) AST stanfart double operator."""

    def get_value(self) -> int:
        ...


class AstPow(AstOperatorDoubleBracket[float]):
    """Power (float) AST stanfart double operator."""

    def get_value(self) -> float:
        ...


class AstLshift(AstOperatorDoubleBracket[int]):
    """Bitwise shift left AST bracket double operator."""

    def get_value(self) -> int:
        ...


class AstRshift(AstOperatorDoubleBracket[int]):
    """Bitwise shift right AST bracket double operator."""

    def get_value(self) -> int:
        ...


class AstAnd(AstCanBeBool[NT]):
    """Bitwise and logical and AST CanBeBool operator."""

    def get_value(self) -> NT:
        ...

    def __bool__(self) -> bool:
        ...


class AstOr(AstCanBeBool[NT]):
    """Bitwise or logical and AST CanBeBool operator."""

    def get_value(self) -> NT:
        ...

    def __bool__(self) -> bool:
        ...


class OperatorComparisson(  # type: ignore
        AstOperatorDoubleStandart[NT], AstBool[NT]):
    """Base class for "just boolean" AST operators."""

    def expand(self) -> str:
        """Sets context to bool with invocation."""
        ...

    def get_value(self) -> ty.NoReturn:
        ...


class AstEq(OperatorComparisson[NT]):
    """Equals AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstNe(OperatorComparisson[NT]):
    """Not equals AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstLt(OperatorComparisson[NT]):
    """Less than AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstGt(OperatorComparisson[NT]):
    """Greater than AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstLe(OperatorComparisson[NT]):
    """Less or equal AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstGe(OperatorComparisson[NT]):
    """Greater or equal AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class Arr(VarParent, ty.Generic[KT]):
    """Generic KSP array class.

    * value can be as list of generic, as well as generic itself
        e.g. declare array[size] := (val)
    * name can be optional if array is not local
    * size is optional, but it helps to keep self in broads"""

    _value: ty.List[KT]  # type: ignore
    _vars: ty.List[ty.Optional[VarParent[KT]]]
    _init_size: int
    _size: int
    _init_seq: ty.List[KT]
    _default: KT
    _recieved_rt: bool

    def __init__(
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
        ...

    def _after_init(self, value: ty.List[KT]) -> None:
        ...

    def _resolve_idx(self, idx: NTU[int]) -> ty.Tuple[str, int]:
        """Return tuple of str(idx) and RT(idx)."""
        ...

    def __getitem__(self, idx: NTU[int]) -> VarParent[KT]:
        """Return Var[self._ref_type] instance, bounded to the cell at idx."""
        ...

    def __setitem__(self, idx: NTU[int], value: VarParent[KT]) -> None:
        """Assign bounded var to array cell."""
        ...

    def _get_cashed_item(self, c_idx: str, r_idx: int) -> VarParent[KT]:
        """Return cashed var from cell with modified str idx.

        or cash (instantiate) one."""
        ...

    def _get_type_prefix(self) -> str:
        """Arr representation of the same Var method."""
        ...

    def _gen_decl_seq_item(self, idx: int, i: KT) -> str:
        """Decl_line halper function."""
        ...

    def get_decl_line(self) -> ty.List[str]:
        """Return declaration line with as much inlined values as possible."""
        ...

    def __ilshift__(self, other: ATU[KT]) -> ty.NoReturn:
        """Raise NotImplementedError."""
        ...

    def __len__(self) -> int:
        """Return current RT length of array."""
        ...

    def _append_is_possible(self) -> bool:
        """Check if append is possible.

        Raises RuntimeError"""
        ...

    def append(self, value: ATU[KT]) -> None:
        """Append value to array, if it is still init cb."""
        ...

    @property
    def val(self) -> ty.List[KT]:
        """Return RT value of Var or Arr."""

    @val.setter
    def val(self, val: KT) -> None:
        """Set RT value of Var or Arr.

        accepts only generics: int, str, float."""
