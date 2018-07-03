from abc import ABCMeta
from abc import abstractmethod
# from abstract import KSP
# from interfaces import IOutput
# from dev_tools import Infix

# from native_types import kInt
# from native_types import kStr
# from native_types import kReal
# from native_types import kArrInt
# from native_types import kArrStr
# from native_types import kArrReal
# from native_types import KspNativeArray


class AstMethod(metaclass=ABCMeta):
    '''abstract AST class for handle various KSP code-generation
    basic usage of any AST object is:
        master_obj = AstObject(*args)()
        IOutput.put(master_obj)
    For proper handling lines IOutput.put has to be called ones per
    line. Other Ast objects has to be returned into master_obj.
    '''
    bool_line = False

    def __init__(self, *args):
        self.args = list(args)

    def __call__(self, value=None):
        # if value:
        #     return AstAsgn(self, value)()
        return self.method()

    @abstractmethod
    def method(self):
        pass


class AstBool(AstMethod):

    def method(self):
        pass

    def __call__(self, condition):
        AstMethod.bool_line = True
        out = condition()
        AstMethod.bool_line = False
        return out


class AstOperator(AstMethod):
    '''The main AST class, handling standart, unary, binary
    operators which KSP accepts.
    subclassing:
        class SubClass(AstOperator):
            def method(self[, other]):
                # returns "self operator_str other"
                return self.operator(operator_str: str)

                # or
                # returns "operator_str(self, other)"
                return self.operator_bracket_double(
                    operator_str: str)

                # or
                # returns "operator_str(self)"
                return self.operator_unary(string)

    '''

    def operator(self, string):
        out = list()
        for idx, arg in enumerate(self.args):
            if idx != 0:
                out.append(string)
            if callable(arg):
                out.append(arg())
            else:
                out.append(str(arg))

        out_str = str()
        for item in out:
            out_str += str(item)
        return out_str

    def operator_bracket_double(self, string):
        out = list()
        for idx, arg in enumerate(self.args):
            if idx != 0:
                out.append(', ')
            if callable(arg):
                out.append(arg())
            else:
                out.append(str(arg))

        out_str = str()
        for item in out:
            out_str += item
        out_str = '%s(%s)' % (string, out_str)
        # IOutput.put(out_str)
        return out_str

    def operator_unary(self, string):
        if callable(self.args[0]):
            return '%s(%s)' % (string, self.args[0]())
        return '%s%s' % (string, self.args[0])

    def magic_straight(self, other, pure, ast):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1].pure(other)
            return self
        else:
            return ast(self, other)

    def __neg__(self):
        return AstNeg(self)

    def __invert__(self):
        return AstNot(self)

    def __add__(self, other):
        # if type(self.args[1]) == type(other):
        #     self.args[1] = self.args[1] + other
        #     return self

        return AstAdd(self, other)

    def __radd__(self, other):
        return AstAdd(other, self)

    def __iadd__(self, other):
        return AstAdd(self + self, other)

    def __sub__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] - other
            return self
        else:
            return AstSub(self, other)

    def __rsub__(self, other):
        return AstSub(other, self)

    def __isub__(self, other):
        return AstSub(self - self, other)

    def __mul__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] * other
            return self
        else:
            return AstMul(self, other)

    def __rmul__(self, other):
        return AstMul(other, self)

    def __imul__(self, other):
        return AstMul(self * self, other)

    def __truediv__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] / other
            return self
        else:
            return AstDiv(self, other)

    def __rtruediv__(self, other):
        return AstDiv(other, self)

    def __itruediv__(self, other):
        return AstDiv(self / self, other)

    def __floordiv__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] // other
            return self
        else:
            return AstDiv(self, other)

    def __rfloordiv__(self, other):
        return AstDiv(other, self)

    def __ifloordiv__(self, other):
        return AstDiv(self // self, other)

    def __mod__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] % other
            return self
        else:
            return AstMod(self, other)

    def __rmod__(self, other):
        return AstMod(other, self)

    def __imod__(self, other):
        return AstMod(self % self, other)

    def __pow__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] ** other
            return self
        else:
            return AstPow(self, other)

    def __rpow__(self, other):
        return AstPow(other, self)

    def __ipow__(self, other):
        return AstPow(self ** self, other)

    def __lshift__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] << other
            return self
        else:
            return AstLshift(self, other)

    def __rlshift__(self, other):
        return AstLshift(other, self)

    def __ilshift__(self, other):
        return AstLshift(self << self, other)

    def __rshift__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] >> other
            return self
        else:
            return AstRshift(self, other)

    def __rrshift__(self, other):
        return AstRshift(other, self)

    def __irshift__(self, other):
        return AstRshift(self >> self, other)

    def __and__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] & other
            return self
        # if AstMethod.bool_line:
        #     return AstLogAnd(self, other)
        return AstAnd(self, other)

    def __rand__(self, other):
        return AstAnd(other, self)

    def __iand__(self, other):
        return AstAnd(self & self, other)

    def __or__(self, other):
        if type(self.args[1]) == type(other):
            self.args[1] = self.args[1] | other
            return self
        return AstOr(self, other)
        # return False

    def __ror__(self, other):
        return lambda self=self, other=other: AstOr(other, self)

    def __ior__(self, other):
        return AstOr(self | self, other)

    def __eq__(self, other):
        return AstEq(self, other)

    def __ne__(self, other):
        return AstNe(self, other)

    def __lt__(self, other):
        return AstLt(self, other)

    def __gt__(self, other):
        return AstGt(self, other)

    def __le__(self, other):
        return AstLe(self, other)

    def __ge__(self, other):
        return AstGe(self, other)

    # def __bool__(self):
    #     return AstBool()(self)


class AstNeg(AstOperator):

    def method(self):
        return self.operator_unary('-')


class AstNot(AstOperator):

    def method(self):
        return self.operator_unary('.not.')


class AstAdd(AstOperator):

    def method(self):
        return self.operator(' + ')


class AstAddString(AstOperator):

    def method(self):
        return self.operator(' & ')


class AstSub(AstOperator):

    def method(self):
        return self.operator(' - ')


class AstMul(AstOperator):

    def method(self):
        return self.operator(' * ')


class AstDiv(AstOperator):

    def method(self):
        return self.operator(' / ')


class AstMod(AstOperator):

    def method(self):
        return self.operator(' mod ')


class AstPow(AstOperator):

    def method(self):
        return self.operator_bracket_double('pow')


class AstLshift(AstOperator):

    def method(self):
        return self.operator_bracket_double('sh_left')


class AstRshift(AstOperator):

    def method(self):
        return self.operator_bracket_double('sh_right')


class AstAnd(AstOperator):

    def method(self):
        if AstMethod.bool_line:
            return self.operator(' and ')
        return self.operator(' .and. ')


class AstOr(AstOperator):

    def method(self):
        if AstMethod.bool_line:
            return self.operator(' or ')
        return self.operator(' .or. ')


class AstEq(AstOperator):

    def method(self):
        return self.operator(' = ')


class AstNe(AstOperator):

    def method(self):
        return self.operator(' # ')


class AstLt(AstOperator):

    def method(self):
        return self.operator(' < ')


class AstGt(AstOperator):

    def method(self):
        return self.operator(' > ')


class AstLe(AstOperator):

    def method(self):
        return self.operator(' <= ')


class AstGe(AstOperator):

    def method(self):
        return self.operator(' >= ')


class AstAsgn(AstOperator):

    def method(self):
        return self.operator(' := ')


class AstGetItem(AstOperator):

    def method(self):

        iterable = self.args[0]
        idx = self.args[1]
        if callable(idx):
            idx = idx()
        return f'{iterable.name()}[{idx}]'

    def __add__(self, other):
        if isinstance(other, str):
            return AstAddString(self, other)
        return AstAdd(self, other)

    def __iadd__(self, other):
        if isinstance(other, str):
            return AstAsgn(AstAddString(self, other))
        return AstAsgn(AstAdd(self, other))

    def __radd__(self, other):
        if isinstance(other, str):
            return AstAddString(other, self)
        return AstAdd(other, self)

    def __sub__(self, other):
        return AstSub(self, other)

    def __mul__(self, other):
        return AstMul(self, other)

    def __truediv__(self, other):
        return AstDiv(self, other)

    def __floordiv__(self, other):
        return AstDiv(self, other)

    def __mod__(self, other):
        return AstMod(self, other)

    def __pow__(self, other):
        return AstPow(self, other)

    def __lshift__(self, other):
        return AstLshift(self, other)

    def __rshift__(self, other):
        return AstRshift(self, other)

    def __and__(self, other):
        return AstAnd(self, other)

    def __or__(self, other):
        return AstOr(self, other)

    def __isub__(self, other):
        return AstAsgn(AstSub(self, other))

    def __imul__(self, other):
        return AstAsgn(AstMul(self, other))

    def __itruediv__(self, other):
        return AstAsgn(AstDiv(self, other))

    def __ifloordiv__(self, other):
        return AstAsgn(AstDiv(self, other))

    def __imod__(self, other):
        return AstAsgn(AstMod(self, other))

    def __ipow__(self, other):
        return AstAsgn(AstPow(self, other))

    def __ilshift__(self, other):
        return AstAsgn(AstLshift(self, other))

    def __irshift__(self, other):
        return AstAsgn(AstRshift(self, other))

    def __iand__(self, other):
        return AstAsgn(AstAnd(self, other))

    def __ior__(self, other):
        return AstAsgn(AstOr(self, other))


class AstSetItem(AstGetItem):

    def method(self):
        iterable = self.args[0]
        idx = self.args[1]
        value = self.args[2]
        if callable(idx):
            idx = idx()
        # out = self.return_item_type(iterable, idx)
        return AstAsgn(f'{iterable.name()}[{idx}]', value)()


class AstLogAnd(AstOperator):

    def method(self):
        return self.operator(' and ')


class AstLogOr(AstOperator):

    def method(self):
        return self.operator(' or ')
