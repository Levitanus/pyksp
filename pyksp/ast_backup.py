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