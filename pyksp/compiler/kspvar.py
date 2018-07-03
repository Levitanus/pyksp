

from abstract import KspObject
from abstract import KSP
from pyksp_ast import *
from interfaces import IOutput


class KspVarObj(KspObject):
    '''
    Abstract class for all KSP objects
    can be used as variables:
        - variables
        - arrays
        - built-ins
    '''

    def __init__(self, full_name: str, value=None,
                 preserve_name: bool=False):
        super().__init__(full_name, preserve_name)
        self._value = value

    def value_set(self, value):
        if isinstance(value, KspVarObj):
            value = value.value_get()
        self._value = value

    def value_get(self):
        return self._value

    def __call__(self, value=None):
        if value is not None:
            self.value_set(value)
            self._ast_assign(value)
            return
        if self.is_under_test():
            return self.value_get()
        return self.name()

    def _ast_assign(self, val):
        '''shortcut to IOutput.put(AstAsgn(self.name(), val)()'''
        IOutput.put(AstAsgn(self.name(), val)())

    def __neg__(self):
        if self.is_under_test():
            return -self.value_get()
        return AstNeg(self.name())

    def __invert__(self):
        if self.is_under_test():
            return ~self.value_get()
        return AstNot(self.name())

    def __add__(self, other):
        if self.is_under_test():
            return self.value_get() + other
        return AstAdd(self.name(), other)

    def __radd__(self, other):
        if self.is_under_test():
            return other + self.value_get()
        return AstAdd(other, self.name())

    def __iadd__(self, other):
        self.value_set(self.value_get() + other)
        if not self.is_under_test():
            self._ast_assign(AstAdd(self.name(), other))
        return self

    def __sub__(self, other):
        if self.is_under_test():
            return self.value_get() - other
        return AstSub(self.name(), other)

    def __rsub__(self, other):
        if self.is_under_test():
            return other - self.value_get()
        return AstSub(other, self.name())

    def __isub__(self, other):
        self._value = self._value - other
        if not self.is_under_test():
            self._ast_assign(AstSub(self.name(), other))
        return self

    def __mul__(self, other):
        if self.is_under_test():
            return self.value_get() * other
        return AstMul(self.name(), other)

    def __rmul__(self, other):
        if self.is_under_test():
            return other * self.value_get()
        return AstMul(other, self.name())

    def __imul__(self, other):
        self._value = self._value * other
        if not self.is_under_test():
            self._ast_assign(AstMul(self.name(), other))
        return self

    def __truediv__(self, other):
        if self.is_under_test():
            return self.value_get() / other
        return AstDiv(self.name(), other)

    def __rtruediv__(self, other):
        if self.is_under_test():
            return other / self.value_get()
        return AstDiv(other, self.name())

    def __itruediv__(self, other):
        self._value = self._value / other
        if not self.is_under_test():
            self._ast_assign(AstDiv(self.name(), other))
        return self

    def __floordiv__(self, other):
        if self.is_under_test():
            return self.value_get() // other
        return AstDiv(self.name(), other)

    def __rfloordiv__(self, other):
        if self.is_under_test():
            return other // self.value_get()
        return AstDiv(other, self.name())

    def __ifloordiv__(self, other):
        self._value = self._value // other
        if not self.is_under_test():
            self._ast_assign(AstDiv(self.name(), other))
        return self

    def __mod__(self, other):
        if self.is_under_test():
            return self.value_get() % other
        return AstMod(self.name(), other)

    def __rmod__(self, other):
        if self.is_under_test():
            return other % self.value_get()
        return AstMod(other, self.name())

    def __imod__(self, other):
        self._value = self._value % other
        if not self.is_under_test():
            self._ast_assign(AstMod(self.name(), other))
        return self

    def __pow__(self, other):
        if self.is_under_test():
            return self.value_get() ** other
        return AstPow(self.name(), other)

    def __rpow__(self, other):
        if self.is_under_test():
            return other ** self.value_get()
        return AstPow(other, self.name())

    def __ipow__(self, other):
        self._value = self._value ** other
        if not self.is_under_test():
            self._ast_assign(AstPow(self.name(), other))
        return self

    def __lshift__(self, other):
        if self.is_under_test():
            return self.value_get() << other
        return AstLshift(self.name(), other)

    def __rlshift__(self, other):
        if self.is_under_test():
            return other << self.value_get()
        return AstLshift(other, self.name())

    def __ilshift__(self, other):
        self._value = self._value << other
        if not self.is_under_test():
            self._ast_assign(AstLshift(self.name(), other))
        return self

    def __rshift__(self, other):
        if self.is_under_test():
            return self.value_get() >> other
        return AstRshift(self.name(), other)

    def __rrshift__(self, other):
        if self.is_under_test():
            return other >> self.value_get()
        return AstRshift(other, self.name())

    def __irshift__(self, other):
        self._value = self._value >> other
        if not self.is_under_test():
            self._ast_assign(AstRshift(self.name(), other))
        return self

    def __and__(self, other):
        if self.is_under_test():
            if KSP.is_bool():
                return self.value_get() and other
            return self.value_get() & other
        return AstAnd(self.name(), other)

    def __rand__(self, other):
        if self.is_under_test():
            if KSP.is_bool():
                return self.value_get() and other
            return other & self.value_get()
        return AstAnd(other, self.name())

    def __iand__(self, other):
        self._value = self._value & other
        if not self.is_under_test():
            self._ast_assign(AstAnd(self.name(), other))
        return self

    def __or__(self, other):
        if self.is_under_test():
            if KSP.is_bool():
                return self.value_get() or other
            return self.value_get() | other
        return AstOr(self.name(), other)

    def __ror__(self, other):
        if self.is_under_test():
            if KSP.is_bool():
                return self.value_get() or other
            return other | self.value_get()
        return AstOr(other, self.name())

    def __ior__(self, other):
        self._value = self._value | other
        if not self.is_under_test():
            self._ast_assign(AstOr(self.name(), other))
        return self

    def __eq__(self, other):
        if self.is_under_test():
            return self.value_get() == other
        return AstEq(self.name(), other)

    def __ne__(self, other):
        if self.is_under_test():
            return self.value_get() != other
        return AstNe(self.name(), other)

    def __lt__(self, other):
        if self.is_under_test():
            return self.value_get() < other
        return AstLt(self.name(), other)

    def __gt__(self, other):
        if self.is_under_test():
            return self.value_get() > other
        return AstGt(self.name(), other)

    def __le__(self, other):
        if self.is_under_test():
            return self.value_get() <= other
        return AstLe(self.name(), other)

    def __ge__(self, other):
        if self.is_under_test():
            return self.value_get() >= other
        return AstGe(self.name(), other)
