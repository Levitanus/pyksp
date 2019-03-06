"""Base KSP types and compiler mechanics."""
import typing as ty
from functools import singledispatch
from abc import abstractmethod

from .abstract import KspObject
from .abstract import NameBase
from .abstract import NameVar
from .abstract import AstRoot
from .abstract import AstString
from .abstract import AstBase
from .abstract import HasInit
from .abstract import KSP

T = ty.TypeVar("T")
KT = ty.TypeVar("KT", int, float, str)
NT = ty.TypeVar("NT", int, float)
VHT = ty.TypeVar(
    'VHT',
    int,
    str,
    float,
    ty.List[int],
    ty.List[str],
    ty.List[float]
)
KLT = ty.TypeVar('KLT', ty.List[int], ty.List[str], ty.List[float])

KVT = ty.TypeVar('KVT', bound='VarBase')
KVT_1 = ty.TypeVar('KVT_1', bound='VarBase')
KAT = ty.TypeVar('KAT', bound=ty.Union['ArrBase'])
KVAT = ty.TypeVar('KVAT', bound=ty.Union['VarBase', 'ArrBase'])

ATU = ty.Union["VarBase[KT, KT]", "AstBase[KT]", "Magic[KT]", KT]
NVU = ty.Union["AstBase[KT]", "Magic[KT]", KT]
STU = ty.Union["VarBase[KT, KT]", "AstBase[KT]", "Magic[KT]", str]
NTU = ty.Union[NT, "ProcessNum[NT]"]
PNT = ty.TypeVar("PNT", bound='ProcessNum', covariant=True)
PNTI = ty.TypeVar("PNTI", bound='ProcessNum[int]', covariant=True)
PNTF = ty.TypeVar("PNTF", bound='ProcessNum[float]', covariant=True)
NFT = ty.TypeVar("NFT", bound=ty.Callable[..., ty.Any])

VarIU = ty.Union[ty.Type[int], ty.Type[str], ty.Type[float]]
VarRU = ty.Union[ty.Type["VarInt"],
                 ty.Type["VarFloat"],
                 ty.Type["VarStr"]]
ArrRU = ty.Type[ty.Union["ArrInt", "ArrFloat", "ArrStr"]]


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
    _ref_type: ty.Type[KT]


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

    _ref_type: ty.Type[str]
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


def ducktype_num_magic(method: NFT) -> NFT:
    """Check that ref_type of other is campatible with self."""
    ...


class ProcessNum(Magic[NT]):
    """Base class for objects, keeps int and float values."""

    def __neg__(self) -> "AstNeg[NT]":
        """Return AstNeg object."""
        ...

    def __pos__(self) -> ty.NoReturn:
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
    def __lt__(self, other: NTU[NT]) -> "AstLt[NT]":  # type: ignore
        """Return AstLt object.

        note: AstLt is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstLt)"""
        ...

    @ducktype_num_magic
    def __gt__(self, other: NTU[NT]) -> "AstGt[NT]":  # type: ignore
        """Return AstGt object.

        note: AstGt is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstGt)"""
        ...

    @ducktype_num_magic
    def __le__(self, other: NTU[NT]) -> "AstLe[NT]":  # type: ignore
        """Return AstLe object.

        note: AstLe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstLe)"""
        ...

    @ducktype_num_magic
    def __ge__(self, other: NTU[NT]) -> "AstGe[NT]":  # type: ignore
        """Return AstGe object.

        note: AstGe is not equal bool, but can be used in if-conditions
        and their RT value retrieved withi bool(AstGe)"""
        ...

    def __abs__(self) -> "AstAbs[NT]":
        """Return AstAbs[self._ref_type] object."""
        ...


class ProcessInt(ProcessNum[int]):
    def __invert__(self) -> "AstNot":
        """Return AstNot object if self ref is int."""
        ...

    def __mod__(self, other: NTU[int]) -> "AstMod":
        """Return AstMod object if self._ref_type is int."""
        ...

    def __rmod__(self, other: NTU[int]) -> "AstMod":
        """Return AstMod object if self._ref_type is int."""
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


class ProcessFloat(ProcessNum[float]):
    def to_int(self) -> "AstInt":
        """Return AstInt object if self._ref_type is float."""
        ...

    def __pow__(self, other: NTU[float]) -> "AstPow":
        """Return AstPow object if self._ref_type is float."""
        ...

    def __rpow__(self, other: NTU[float]) -> "AstPow":
        """Return AstPow object if self._ref_type is float."""
        ...


def to_int(value: ProcessFloat) -> "AstInt":
    """Return AstInt object if value._ref_type is float."""
    ...


def to_float(value: ProcessInt) -> "AstFloat":
    """Return AstFloat object if value._ref_type is int."""
    ...


class ValueHolder(ty.Generic[VHT]):
    """Simple value holder, can be transfered between variables."""

    def __init__(self, value: VHT) -> None:
        ...

    def set(self, value: VHT) -> None:
        """Set value to holder."""
        ...

    def get(self) -> VHT:
        """Get value from holder."""
        ...


class VarBase(KspObject, HasInit, ty.Generic[VHT, KT], Magic[KT]):
    """Base Generic class for every KSP object, recieves values.

    keeps self._ref_type, representing it's generic parent.
    generates init lines, if not declared as local."""
    names_count: int = 0
    _persist: 'Persist'
    _array: ty.Optional['ArrBase']
    _idx: ty.Optional[int]
    _value: ValueHolder[VHT]
    _init_val: VHT

    class Persist:
        """Class for mark persistence of variable.

        can be:
        VarBase.not_persistent
        VarBase.persistent
        VarBase.inst_persistent
        VarBase.read_persistent"""

        line: str

        def __init__(self, line: str = "") -> None:
            ...

    not_persistent: ty.ClassVar[Persist] = Persist()
    persistent: ty.ClassVar[Persist] = Persist("make_persistent")
    inst_persistent: ty.ClassVar[Persist] = Persist(
        "make_instr_persistent"
    )
    read_persistent: ty.ClassVar[Persist] = Persist("make_persistent")

    def __init__(
        self,
        value: VHT,
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

    def _bound_to_array(
        self,
        array: 'ArrBase[KVT, VHT, KT]',
        idx: int
    ) -> None:
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
    def val(self) -> VHT:
        """Return RT value of Var or Arr."""
        ...

    @val.setter
    def val(self, val: VHT) -> None:
        """Set RT value of Var or Arr.

        accepts only generics: int, str, float."""
        ...

    def read(self) -> None:
        """Read persistent val in init cb.

        makes var persistent, if not."""
        ...

    def copy(self, name: str, prefix: str, postfix: str) -> KVT:
        """Return new object of self type.

        For arr cells obj._array and obj._idx are loosed.
        init_val is loosed."""
        ...

    def _make_copy(
        self,
        other: ty.Union[NVU,
                        'VarBase[KT, KT]'],
        value: VHT,
        new_type: ty.Type[KVT]
    ) -> KVT:
        """Return new Var[self._ref_type] object, depends on input val."""
        ...

    @staticmethod
    def refresh() -> None:
        """Refresh Var autogenerated names."""
        ...


STT = (VarBase, str, ConcatsStrings)


class VarStr(VarBase[str, str], ConcatsStrings):
    """String KSP Var."""

    def __init__(
        self,
        value: str = "",
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
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

    def __ilshift__(self: KVT_1, other: STU) -> KVT_1:
        """Return new Str object with name of self and value of other."""
        ...

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] of simple declaration."""
        ...

    def __iadd__(self: KVT_1, other: STU) -> KVT_1:  # type: ignore
        """Return new Str object, keep concatenated self+string."""
        ...


class Num(VarBase[NT, NT], ProcessNum[NT], ty.Generic[NT, KVT]):
    """Generic KSP numeric Var (int or float)."""
    _ref_type: ty.Type[NT]

    def __init__(
        self,
        value: NT,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        *,
        local: bool = False
    ) -> None:
        """Initialize.

        Value is Optional if instantiated within indexation[]
        name is strict if local=True
        persist can be optional if read() method called
        local only for internal library usage."""
        ...

        ...

    def get_decl_line(self) -> ty.List[str]:
        """Return List[str] of simple declaration."""
        ...

    @ducktype_num_magic
    def __iadd__(self: KVT_1, other: NTU[NT]) -> KVT_1:  # type: ignore
        ...

    @ducktype_num_magic
    def __isub__(self: KVT_1, other: NTU[NT]) -> KVT_1:  # type: ignore
        ...

    @ducktype_num_magic
    def __imul__(self: KVT_1, other: NTU[NT]) -> KVT_1:  # type: ignore
        ...

    @ducktype_num_magic
    def __itruediv__(  # type: ignore
        self: KVT_1,
        other: NTU[NT]
    ) -> KVT_1:
        ...

    def __iand__(self, other: NTU[NT]) -> ty.NoReturn:
        ...

    def __ior__(self, other: NTU[NT]) -> ty.NoReturn:
        ...


class VarInt(Num[int, "VarInt"], ProcessInt):
    def __init__(
        self,
        value: int = 0,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        *,
        local: bool = False
    ) -> None:
        ...

    def __ilshift__(  # type: ignore
        self: KVT_1,
        other: ATU[NT]
    ) -> KVT_1:
        """Return new Num[self._ref_type] object.

        with name of self and value of other."""

    @ducktype_num_magic
    def __imod__(self: KVT_1, other: NTU[int]) -> KVT_1:  # type: ignore
        ...

    def inc(self) -> None:
        """Increase value by 1, if int."""
        ...

    def dec(self) -> None:
        """Decrease value by 1, if int."""
        ...


class VarFloat(Num[float, "VarFloat"], ProcessFloat):
    def __init__(
        self,
        value: float = 0.0,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        *,
        local: bool = False
    ) -> None:
        ...

    def __ilshift__(self: KVT_1, other: ATU[NT]) -> KVT_1:
        """Return new Num[self._ref_type] object.

        with name of self and value of other."""

    @ducktype_num_magic
    def __ipow__(  # type: ignore
        self: KVT_1,
        other: NTU[float]
    ) -> KVT_1:
        ...


def _assert_Num_int(var: NTU[int]) -> None:
    """Raise TypeError if not int or KspInt passed."""
    ...


def inc(var: Num[int, 'VarInt']) -> None:
    """Increase value by 1, if int."""
    ...


def dec(var: Num[int, 'VarInt']) -> None:
    """Decrease value by 1, if int."""
    ...


class ArrBase(VarBase[VHT, KT], ty.Generic[KVT, VHT, KT]):
    """Generic KSP array class.

    * value can be as list of generic, as well as generic itself
        e.g. declare array[size] := (val)
    * name can be optional if array is not local
    * size is optional, but it helps to keep self in broads"""

    _value: ValueHolder[VHT]
    _vars: ty.List[ty.Optional[KVT]]
    _init_size: ty.Optional[int]
    _size: int
    _init_seq: ty.List[KT]
    _default: KT
    _recieved_rt: bool

    def __getitem__(self, idx: NTU[int]) -> KVT:
        """Return Var[self._ref_type] instance, bounded to the cell at idx."""
        ...

    def __setitem__(self, idx: NTU[int], value: KVT) -> None:
        """Assign bounded var to array cell."""
        ...

    def _get_cashed_item(self, c_idx: str, r_idx: int) -> KVT:
        """Return cashed var from cell with modified str idx.

        or cash (instantiate) one."""
        ...

    def __init__(
        self,
        value: VHT,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
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

    def _resolve_idx(self, idx: NTU[int]) -> ty.Tuple[str, int]:
        """Return tuple of str(idx) and RT(idx)."""
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

    def __iter__(self) -> ty.NoReturn:
        ...


class ArrStr(ArrBase[VarStr, ty.List[str], str]):
    def __init__(
        self,
        value: ty.Union[str,
                        ty.List[str]] = "",
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> None:
        ...


class ArrInt(ArrBase[VarInt, ty.List[int], int]):
    def __init__(
        self,
        value: ty.Union[int,
                        ty.List[int]] = 0,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> None:
        ...


class ArrFloat(ArrBase[VarFloat, ty.List[float], float]):
    def __init__(
        self,
        value: ty.Union[float,
                        ty.List[float]] = 0.0,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> None:
        ...


class VarMeta(type):
    """Var getitem helper metaclass."""

    @ty.overload
    def __getitem__(cls, ref: ty.Type[int]) -> ty.Type["VarInt"]:
        ...

    @ty.overload
    def __getitem__(cls, ref: ty.Type[float]) -> ty.Type["VarFloat"]:
        ...

    @ty.overload
    def __getitem__(cls, ref: ty.Type[str]) -> ty.Type["VarStr"]:
        ...

    @ty.overload
    def __getitem__(cls,
                    ref: ty.Tuple[VarIU,
                                  int]) -> ty.Type['ArrType']:
        ...

    def __instancecheck__(cls, inst: object) -> bool:
        ...


class Var(metaclass=VarMeta):
    @ty.overload
    def __new__(
        cls,
        value: int,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        *,
        local: bool = False,
    ) -> 'VarInt':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
        cls,
        value: float,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        *,
        local: bool = False,
    ) -> 'VarFloat':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
        cls,
        value: str,
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        *,
        local: bool = False,
    ) -> 'VarStr':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
        cls,
        value: ty.List[int],
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> 'ArrInt':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
        cls,
        value: ty.List[float],
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> 'ArrFloat':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
        cls,
        value: ty.List[str],
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> 'ArrStr':
        """Return new object of proper base concrete class."""
        ...


class ArrMeta(type):
    """Var getitem helper metaclass."""

    @ty.overload
    def __getitem__(cls, ref: ty.Type[int]) -> ty.Type["ArrInt"]:
        ...

    @ty.overload
    def __getitem__(cls, ref: ty.Type[float]) -> ty.Type["ArrFloat"]:
        ...

    @ty.overload
    def __getitem__(cls, ref: ty.Type[str]) -> ty.Type["ArrStr"]:
        ...

    @ty.overload
    def __getitem__(cls,
                    ref: ty.Tuple[VarIU,
                                  int]) -> ty.Type['ArrType']:
        ...

    def __instancecheck__(cls, inst: object) -> bool:
        ...


class ArrTypeMeta(type):
    """Extensive instance-checker for ArrBase."""

    def __instancecheck__(cls, obj: object) -> bool:
        ...


class ArrType(metaclass=ArrTypeMeta):
    """Class to be used for pretty instance-checking of Arrays."""
    size: ty.Optional[int] = None
    ref_type: ty.Type[ty.Union[int, str, float]] = int


class Arr(metaclass=ArrMeta):
    @ty.overload
    def __new__(
        cls,
        value: ty.List[int],
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> 'ArrInt':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
        cls,
        value: ty.List[float],
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> 'ArrFloat':
        """Return new object of proper base concrete class."""
        ...

    @ty.overload
    def __new__(
        cls,
        value: ty.List[str],
        name: str = "",
        persist: VarBase.Persist = VarBase.not_persistent,
        preserve_name: bool = False,
        size: ty.Optional[int] = None,
        *,
        local: bool = False,
    ) -> 'ArrStr':
        """Return new object of proper base concrete class."""
        ...


class AstAssign(AstRoot[KT]):
    """Root AST representing assignement."""

    to_arg: "VarBase[KT,KT]"
    from_arg: ATU

    def __init__(
        self,
        to_arg: "VarBase[KT,KT]",
        from_arg: ATU[KT]
    ) -> None:
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

    def __init__(
        self,
        ret_val: ty.Optional[KT],
        string: str,
        *args: ATU
    ) -> None:
        ...

    def expand(self) -> str:
        """Return string representation of AST."""
        ...

    def get_value(self) -> KT:
        """If ret_val, error is not raised."""
        ...


class AstOperatorUnary(  # type: ignore
    AstBase[NT],
    ProcessNum[NT]
):
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


class AstCanBeBool(  # type: ignore
    AstOperatorDoubleStandart[NT],
    AstBool[NT]
):
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


class AstNeg(AstOperatorUnaryStandart[NT], ProcessFloat, ProcessInt):
    """Negative AST operator."""
    string = "-"

    def get_value(self) -> NT:
        """Return -agr."""
        ...


class AstAbs(AstOperatorUnaryBracket[NT], ProcessFloat, ProcessInt):
    """Absolute val operator."""

    def get_value(self) -> NT:
        ...


class AstAdd(AstOperatorDoubleStandart[NT], ProcessFloat, ProcessInt):
    """Addition AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstSub(AstOperatorDoubleStandart[NT], ProcessFloat, ProcessInt):
    """Substitution AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstDiv(AstOperatorDoubleStandart[NT], ProcessFloat, ProcessInt):
    """Division AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstMul(AstOperatorDoubleStandart[NT], ProcessFloat, ProcessInt):
    """Multiplication AST stanfart double operator."""

    def get_value(self) -> NT:
        ...


class AstAnd(AstCanBeBool[NT], ProcessFloat, ProcessInt):
    """Bitwise and logical and AST CanBeBool operator."""

    def get_value(self) -> NT:
        ...

    def __bool__(self) -> bool:
        ...


class AstOr(AstCanBeBool[NT], ProcessFloat, ProcessInt):
    """Bitwise or logical and AST CanBeBool operator."""

    def get_value(self) -> NT:
        ...

    def __bool__(self) -> bool:
        ...


class OperatorComparisson(  # type: ignore
        AstOperatorDoubleStandart[NT], AstBool[NT], ProcessFloat, ProcessInt):
    """Base class for "just boolean" AST operators."""

    def expand(self) -> str:
        """Sets context to bool with invocation."""
        ...

    def get_value(self) -> ty.NoReturn:
        ...


class AstEq(OperatorComparisson[NT], ProcessFloat, ProcessInt):
    """Equals AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstNe(OperatorComparisson[NT], ProcessFloat, ProcessInt):
    """Not equals AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstLt(OperatorComparisson[NT], ProcessFloat, ProcessInt):
    """Less than AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstGt(OperatorComparisson[NT], ProcessFloat, ProcessInt):
    """Greater than AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstLe(OperatorComparisson[NT], ProcessFloat, ProcessInt):
    """Less or equal AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstGe(OperatorComparisson[NT], ProcessFloat, ProcessInt):
    """Greater or equal AST Bool operator."""

    def __bool__(self) -> bool:
        ...


class AstNot(AstOperatorUnaryStandart[int], ProcessInt):
    """Bitwise not AST operator.

    works only for ints."""

    def get_value(self) -> int:
        ...


class AstInt(AstOperatorUnaryBracket[int], ProcessInt):
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


class AstMod(AstOperatorDoubleStandart[int], ProcessInt):
    """Modulo (int) AST stanfart double operator."""

    def get_value(self) -> int:
        ...


class AstLshift(AstOperatorDoubleBracket[int], ProcessInt):
    """Bitwise shift left AST bracket double operator."""

    def get_value(self) -> int:
        ...


class AstRshift(AstOperatorDoubleBracket[int], ProcessInt):
    """Bitwise shift right AST bracket double operator."""

    def get_value(self) -> int:
        ...


class AstFloat(AstOperatorUnaryBracket[float], ProcessFloat):
    """Represent KSP int_to_real function."""
    arg1: NTU[int]  # type: ignore
    arg1_pure: float
    arg1_str: str

    def __init__(self, arg1: NTU[int]) -> None:
        ...

    def get_value(self) -> float:
        """Return float(arg)."""
        ...


class AstPow(AstOperatorDoubleBracket[float], ProcessFloat):
    """Power (float) AST stanfart double operator."""

    def get_value(self) -> float:
        ...
