from abc import abstractmethod
from warnings import warn

from abstract import KspObject
from abstract import KSP
from abstract import Output

from typing import Union


class AstBase(KSP):
    '''Base abstract class for all Ast objects.
    Requires overriding of methods expand() and get_value()

    expand(self) has to return string representation of method
    get_value(self) has to behave like real representation of method
    '''

    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def get_value(self):
        pass


class AstAssign(AstBase):
    '''special top-level Ast class for making assigements.
    Has not method get_value()
    '''

    def __init__(self, to_arg, from_arg):
        if isinstance(to_arg, KspVar):
            self._to_arg = to_arg.name()
            if not self._to_arg:
                raise TypeError('variable val is None')
        else:
            raise TypeError(
                f'can assign only to instance of {KspVar}')
        if isinstance(from_arg, AstAssign):
            raise TypeError('AstAssign is root, can not be added')
        if callable(from_arg):
            self._from_arg = from_arg()
        if isinstance(from_arg, (str, int, float)):
            self._from_arg = from_arg
        elif isinstance(from_arg, AstBase):
            self._from_arg = from_arg.expand()
        elif isinstance(from_arg, KspVar):
            self._from_arg = from_arg.name()
        else:
            raise TypeError('can assign only instances of: %s' % (
                (KspVar, str, int, float, AstBase)
            ))

    def expand(self):
        '''expand AstObject to string representation "a := b"'''
        super().expand()
        return f'{self._to_arg} := {self._from_arg}'

    def get_value(self):
        raise NotImplementedError('AstAssign can not return value')


class AstAddString(AstBase):
    '''special operator method for strings concatenation
    args has to be instances of (callable, str, AstBase, KspVar)
    '''

    def __init__(self, arg1, arg2):
        self._args = [arg1, arg2]

    def expand(self):
        '''returns "a & b"'''
        super().expand()
        args = list()
        for arg in self._args:
            if callable(arg):
                arg = arg()
            if isinstance(arg, str):
                args.append(f'"{arg}"')
                continue
            if isinstance(arg, AstBase):
                args.append(arg.expand())
                continue
            if isinstance(arg, KspVar):
                args.append(f'{arg.val}')
                continue
            raise NotImplementedError('maybe something has to be ' +
                                      f'added to {AstAddString}?')
        return f'{args[0]} & {args[1]}'

    def get_value(self):
        '''returns self.expand()'''
        args = list()
        for arg in self._args:
            if isinstance(arg, str):
                args.append(arg)
                continue
            if isinstance(arg, AstBase):
                args.append(f'{arg.get_value()}')
                continue
            if isinstance(arg, KspVar):
                args.append(f'{arg._get_runtime()}')
                continue
        return args[0] + args[1]

    def __add__(self, other):
        '''returns AstAddString(self, other)'''
        return AstAddString(self, other)

    def __radd__(self, other):
        '''returns AstAddString(other, self)'''
        return AstAddString(other, self)

    def __iadd__(self, other):
        raise NotImplementedError(
            'method __iadd__ is not implemented')


class AstOperator(AstBase):
    '''Base abstract class for all operators.'''

    def __init__(self, *args):
        self._args = args

    def unpack_args(self, *args):
        '''gets values of KspVar objects and expands AstBase objects
        keeps str, int and float objects untouched
        returns tuple of args or only arg, if it was alone
        '''
        new = list()
        for arg in args:
            if isinstance(arg, KspVar):
                arg = arg.val
            if isinstance(arg, AstBase):
                arg = arg.expand()
            if not isinstance(arg, (int, str, float)):
                raise TypeError(
                    f'arg {arg} has to be resolved to str,' +
                    ' int or float')
            new.append(arg)
        if len(new) == 1:
            new = new[0]
        return new

    def unary(self, string: str, val: Union[int, str, float, KspObject]):
        '''returns f"{string}{val}"'''
        val = self.unpack_args(val)
        return f'{string}{val}'

    def standart(self, string: str,
                 val1: Union[int, str, float, KspObject],
                 val2: Union[int, str, float, KspObject]):
        '''returns f"{val1} {string} {val2}"'''
        val1, val2 = self.unpack_args(val1, val2)
        return f'{val1} {string} {val2}'

    def bracket_unary(self, string: str,
                      val: Union[int, str, float, KspObject]):
        '''returns f"{string}({val})"'''
        val = self.unpack_args(val)
        return f'{string}({val})'

    def bracket_double(self, string: str,
                       val1: Union[int, str, float, KspObject],
                       val2: Union[int, str, float, KspObject]):
        '''returns f"{string}({val1}, {val2})"'''
        val1, val2 = self.unpack_args(val1, val2)
        return f'{string}({val1}, {val2})'

    @abstractmethod
    def get_value(self, func):
        '''use via super
        accepts func (lambda?) and passes init args to it.
        args are expanded via:
        _get_runtime() for KspVar objects
        get_value() for AstBase objects'''
        args = list()
        for arg in self._args:
            if isinstance(arg, KspVar):
                arg = arg._get_runtime()
            if isinstance(arg, AstBase):
                arg = arg.get_value()
            args.append(arg)
        return func(*args)

    def __neg__(self):
        return AstNeg(self)

    def __invert__(self):
        return AstNot(self)

    def __add__(self, other):
        return AstAdd(self, other)

    def __radd__(self, other):
        return AstAdd(other, self)

    def __iadd__(self, other):
        raise NotImplementedError(
            'method __iadd__ is not implemented')

    def __sub__(self, other):
        return AstSub(self, other)

    def __rsub__(self, other):
        return AstSub(other, self)

    def __isub__(self, other):
        raise NotImplementedError(
            'method __isub__ is not implemented')

    def __mul__(self, other):
        return AstMul(self, other)

    def __rmul__(self, other):
        return AstMul(other, self)

    def __imul__(self, other):
        raise NotImplementedError(
            'method __imul__ is not implemented')

    def __truediv__(self, other):
        return AstDiv(self, other)

    def __rtruediv__(self, other):
        return AstDiv(other, self)

    def __itruediv__(self, other):
        raise NotImplementedError(
            'method __itruediv__ is not implemented')

    def __floordiv__(self, other):
        raise ArithmeticError('use regular / instead')

    def __rfloordiv__(self, other):
        raise ArithmeticError('use regular / instead')

    def __ifloordiv__(self, other):
        raise NotImplementedError(
            'method __ifloordiv__ is not implemented')

    def __mod__(self, other):
        return AstMod(self, other)

    def __rmod__(self, other):
        return AstMod(other, self)

    def __imod__(self, other):
        raise NotImplementedError(
            'method __imod__ is not implemented')

    def __pow__(self, other):
        return AstPow(self, other)

    def __rpow__(self, other):
        return AstPow(other, self)

    def __ipow__(self, other):
        raise NotImplementedError(
            'method __ipow__ is not implemented')

    def __and__(self, other):
        if self.is_bool():
            return AstLogAnd(self, other)
        return AstBinAnd(self, other)

    def __rand__(self, other):
        if self.is_bool():
            return AstLogAnd(other, self)
        return AstBinAnd(other, self)

    def __or__(self, other):
        if self.is_bool():
            return AstLogOr(self, other)
        return AstBinOr(self, other)

    def __ror__(self, other):
        if self.is_bool():
            return AstLogOr(other, self)

        return AstBinOr(other, self)

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


class AstNeg(AstOperator):

    def expand(self):
        val = self.unpack_args(*self._args)
        return self.unary('-', val)

    def get_value(self):
        return super().get_value(lambda arg: -arg)


class AstNot(AstOperator):
    def expand(self):
        val = self.unpack_args(*self._args)
        return self.unary('.not.', val)

    def get_value(self):
        return super().get_value(lambda arg: ~arg)


class AstAdd(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('+', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 + arg2)


class AstSub(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('-', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 - arg2)


class AstMul(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('*', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 * arg2)


class AstDiv(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('/', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 / arg2)


class AstMod(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('mod', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 & arg2)


class AstPow(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.bracket_double('pow', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 ** arg2)


class AstLogAnd(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('and', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 and arg2)


class AstBinAnd(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        if self.is_bool():
            return self.standart('and', val1, val2)
        return self.standart('.and.', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 & arg2)


class AstLogOr(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('or', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 or arg2)


class AstBinOr(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        if self.is_bool():
            return self.standart('or', val1, val2)
        return self.standart('.or.', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 | arg2)


class AstEq(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('=', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 == arg2)


class AstNe(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('#', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 != arg2)


class AstLt(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('<', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 < arg2)


class AstGt(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('>', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 > arg2)


class AstLe(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('<=', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 <= arg2)


class AstGe(AstOperator):

    def expand(self):
        val1, val2 = self.unpack_args(*self._args)
        return self.standart('>=', val1, val2)

    def get_value(self):
        return super().get_value(lambda arg1, arg2: arg1 >= arg2)


class KspVar(KspObject):
    '''Abstract base class for every object can behave like variable:
    int, string or real(float) variables and arrays of KSP

    abstract methods required:

    @abstractmethod
    def _get_compiled(self)

    @abstractmethod
    def _set_runtime(self, val)

    @abstractmethod
    def _get_runtime(self)

    # can be used via super().val()
    @property
    @abstractmethod
    def val(self):
        if self.is_compiled():
            return self._get_compiled()
        return self._get_runtime()

    also has property for getting and setting value as defaul value
    handler of instantiation via kwarg "value":
    _value

    Strongly reommended to assign kwarg "ref_type". In other case
    KspVar will be used as ref_type.
    '''

    def __init__(self, name, value=None,
                 ref_type=None,
                 name_prefix='',
                 name_postfix='',
                 preserve_name=False,
                 has_init=True, is_local=False,
                 persist=False):
        super().__init__(name, name_prefix=name_prefix,
                         name_postfix=name_postfix,
                         preserve_name=preserve_name,
                         has_init=has_init, is_local=is_local,
                         has_executable=False)
        if ref_type:
            if not isinstance(ref_type, tuple):
                raise TypeError('ref_type has to be tuple of classes')
            for item in ref_type:
                if not isinstance(item, type):
                    raise TypeError('ref_type has to be tuple' +
                                    ' of classes')
            self._ref_type = ref_type
        else:
            self._ref_type = self.__class__

        if value is not None:
            self.__value = self._get_rutime_other(value)
        else:
            self.__value = []
        self._persistent = persist
        self._read = False

    def _check_val_type(self, val):
        '''check if val is instance of ref_type.
        expands val if it is instance of KspVar

        returns val
        '''
        if not isinstance(val, self.ref_type):
            raise TypeError(f'has to be one of: {self.ref_type}.' +
                            f'val ({val}) is of type({type(val)})')
        if isinstance(val, KspVar):
            val = val.val
        return val

    def read(self):
        '''calls KSP function read_persistent_var() and adds
        make_persistent() function call at declaration if not any
        '''
        if not self.in_init():
            raise RuntimeError('can not be outside init')
        if self.is_local:
            raise RuntimeError('is local var')
        if self._read:
            warn('read has been called yet', category=Warning,
                 stacklevel=2)
        Output().put(f'read_persistent_var({self.name()})')
        self._read = True

    @property
    def ref_type(self):
        '''getter. returns tuple of types'''
        return self._ref_type

    def _set_compiled(self, val):
        '''Puts AstAssign to Output()
        calls self._set_runtime with "val" rutime val
        '''
        self._set_runtime(self._get_rutime_other(val))
        Output().put(AstAssign(self, val).expand())

    def _get_rutime_other(self, other):
        '''returns runtime representation of KspVar and AstBase
        or just passed value'''
        if not isinstance(other, self.ref_type):
            raise TypeError(f'has to be one of: {self.ref_type}.' +
                            f'other is of type({type(other)})')
        if hasattr(other, 'get_value'):
            return other.get_value()
        if hasattr(other, '_get_runtime'):
            return other._get_runtime()
        return other

    @abstractmethod
    def _get_compiled(self):
        pass

    @abstractmethod
    def _set_runtime(self, val):
        pass

    @abstractmethod
    def _get_runtime(self):
        pass

    def __ilshift__(self, other):
        '''under compilation calls self._set_compiled
        otherwise calls self._set_runtime

        returns self'''
        self._check_val_type(other)
        if self.is_compiled():
            self._set_compiled(other)
            return self
        self._set_runtime(other)
        return self

    def __rlshift__(self, other):
        '''under compilation calls self._get_compiled
        otherwise calls self._get_runtime
        '''
        if self.is_compiled():
            return self._get_compiled()
        return self._get_runtime()

    @property
    def val(self):
        '''under compilation calls self._get_compiled
        otherwise calls self._get_runtime
        '''
        if self.is_compiled():
            return self._get_compiled()
        return self._get_runtime()

    @property
    def _value(self):
        '''returns value passed in __init__ as "value" parameter'''
        return self.__value

    @_value.setter
    def _value(self, val):
        '''sets the value could be taken from _value property'''
        self._check_val_type(val)
        val = self._get_rutime_other(val)
        self.__value = val


class KspStrVar(KspVar):
    '''Keeps str objects or string representations of KspVar objects
    can be only assigned via <<= or concantenated via + and +=
    '''

    def _set_compiled(self, other):
        if isinstance(other, KspNumeric):
            runtime = f'{other._get_runtime()}'
        else:
            runtime = other
        if isinstance(other, str):
            other = f'"{other}"'
        self._set_runtime(runtime)
        Output().put(AstAssign(self, other).expand())

    def __add__(self, other):
        if self.is_compiled():
            return self._add_compiled(self, other)
        return self._add_runtime(self, other)

    def __radd__(self, other):
        if self.is_compiled():
            return self._add_compiled(other, self)
        return self._add_runtime(other, self)

    def __iadd__(self, other):
        if self.is_compiled():
            add = self._add_compiled(self, other)
            self._set_compiled(add)
            return self
        add = self._add_runtime(self, other)
        self._set_runtime(add)
        return self

    def _add_compiled(self, arg1, arg2):
        return AstAddString(arg1, arg2)

    def _add_runtime(self, arg1, arg2):
        if arg2 is self:
            _arg1 = arg2
            arg2 = arg1
            arg1 = _arg1
        arg1 = self.val
        arg2 = self.__check_add_runtime_str(arg2)
        return arg1 + arg2

    def __check_add_runtime_str(self, other):
        if isinstance(other, KspVar):
            return f'{other.val}'
        if isinstance(other, str):
            return other
        raise TypeError('has to be str')

    def _generate_executable(self):
        raise NotImplementedError('has not to be called')


class KspNumeric(KspVar):
    '''abstract base class for int and real KSP variables
    has to keep class variable "warning_types", consists tuple
    of classes for blocking magic methods.
    For example:
    warning_types = (KspIntVar, str, KspStrVar)

    '''

    warning_types = None
    _warning_types_exc_str =\
        "class var warning_types has to consist tuple of " +\
        'classes to warn within operations'

    # @classmethod
    # def warning_types(cls):
    #     return cls.warning_types

    class TypeWarn(Warning):
        '''raised when type convertion is needed'''

        def __init__(self, val):
            super().__init__(
                f'Value {val} (type{type(val)}) ' +
                'has to be converted within built-in func')

    def __new__(cls, *args, **kwargs):
        '''checks correct assignement of cls.warning_types'''
        if cls.warning_types is None:
            raise TypeError(cls._warning_types_exc_str)
        if not isinstance(cls.warning_types, tuple):
            raise TypeError(cls._warning_types_exc_str)
        for item in cls.warning_types:
            if not isinstance(item, type):
                raise TypeError(cls._warning_types_exc_str)
        obj = super().__new__(cls)
        # obj.__init__(*args, **kwargs)
        return obj

    def _generate_executable(self):
        raise NotImplementedError('has not to be called')

    def _warn_other(self, value):
        if isinstance(value, self.warning_types):
            raise self.TypeWarn(value)

    @abstractmethod
    def __truediv__(self, other):
        pass

    @abstractmethod
    def __rtruediv__(self, other):
        pass

    @abstractmethod
    def __itruediv__(self, other):
        pass

    @abstractmethod
    def __floordiv__(self, other):
        raise ArithmeticError('use regular / instead')

    @abstractmethod
    def __rfloordiv__(self, other):
        raise ArithmeticError('use regular / instead')

    @abstractmethod
    def __ifloordiv__(self, other):
        raise ArithmeticError('use regular / instead')

    def _expand_other(self, other):
        '''returns other, expanded via val property if is
        instance of KspVar'''
        if isinstance(other, self.warning_types):
            raise self.TypeWarn(other)
        if not isinstance(other, self.ref_type):
            raise TypeError(f'has to be one of {self.ref_type}')
        if isinstance(other, (int, str, float)):
            return other
        return other.val

    def __neg__(self):
        if self.is_compiled():
            return AstNeg(self)
        return -self._get_runtime()

    def __invert__(self):
        if self.is_compiled():
            return AstNot(self)
        return ~self._get_runtime()

    def __add__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstAdd(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() + other

    def __radd__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstAdd(other, self)
        other = self._get_runtime_other(other)
        return self._get_runtime() + other

    def __iadd__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            self._set_compiled(AstAdd(self, other))
            return self
        other = self._get_runtime_other(other)
        self._set_runtime(self._get_runtime() + other)
        return self

    def __sub__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstSub(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() - other

    def __rsub__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstSub(other, self)
        other = self._get_runtime_other(other)
        return self._get_runtime() - other

    def __isub__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            self._set_compiled(AstSub(self, other))
            return self
        other = self._get_runtime_other(other)
        self._set_runtime(self._get_runtime() - other)
        return self

    def __mul__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstMul(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() * other

    def __rmul__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstMul(other, self)
        other = self._get_runtime_other(other)
        return self._get_runtime() * other

    def __imul__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            self._set_compiled(AstMul(self, other))
            return self
        other = self._get_runtime_other(other)
        self._set_runtime(self._get_runtime() * other)
        return self

    def __and__(self, other):
        if self.is_compiled():
            if self.is_bool():
                return AstLogAnd(self, other)
            return AstBinAnd(self, other)
        other = self._get_runtime_other(other)
        if self.is_bool():
            return self._get_runtime() and other
        return self._get_runtime() & other

    def __rand__(self, other):
        if self.is_compiled():
            if self.is_bool():
                return AstLogAnd(other, self)
            return AstBinAnd(other, self)
        other = self._get_runtime_other(other)
        if self.is_bool():
            return self._get_runtime() and other
        return self._get_runtime() & other

    def __iand__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        if self.is_compiled():
            if self.is_bool():
                return AstLogOr(self, other)
            return AstBinOr(self, other)
        other = self._get_runtime_other(other)
        if self.is_bool():
            return self._get_runtime() or other
        return self._get_runtime() | other

    def __ror__(self, other):
        if self.is_compiled():
            if self.is_bool():
                return AstLogOr(other, self)
            return AstBinOr(other, self)
        other = self._get_runtime_other(other)
        if self.is_bool():
            return self._get_runtime() or other
        return self._get_runtime() | other

    def __ior__(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        if self.is_compiled():
            return AstEq(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() == other

    def __ne__(self, other):
        if self.is_compiled():
            return AstNe(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() != other

    def __lt__(self, other):
        if self.is_compiled():
            return AstLt(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() < other

    def __gt__(self, other):
        if self.is_compiled():
            return AstGt(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() > other

    def __le__(self, other):
        if self.is_compiled():
            return AstLe(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() <= other

    def __ge__(self, other):
        if self.is_compiled():
            return AstGe(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() >= other

    # def __bool__(self):
    #     if self.is_compiled():
    #         return AstGt(self, 0)
    #     if self._get_runtime() == 0:
    #         return False
    #     return True


class KspIntVar(KspNumeric):

    def __truediv__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstDiv(self, other)
        other = self._get_rutime_other(other)
        return self._get_runtime() // other

    def __rtruediv__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            return AstDiv(other, self)
        other = self._get_rutime_other(other)
        return self._get_runtime() // other

    def __itruediv__(self, other):
        self._warn_other(other)
        if self.is_compiled():
            self._set_compiled(AstDiv(self, other))
            return self
        other = self._get_rutime_other(other)
        self._set_runtime(self._get_runtime() // other)
        return self

    def __floordiv__(self, other):
        return super().__floordiv__(other)

    def __rfloordiv__(self, other):
        return super().__rfloordiv__(other)

    def __ifloordiv__(self, other):
        return super().__ifloordiv__(other)


class KspRealVar(KspNumeric):
    def __truediv__(self, other):
        if self.is_compiled():
            return AstDiv(self, other)
        other = self._get_runtime_other(other)
        return self._get_runtime() / other

    def __rtruediv__(self, other):
        if self.is_compiled():
            return AstDiv(other, self)
        other = self._get_runtime_other(other)
        return self._get_runtime() / other

    def __itruediv__(self, other):
        if self.is_compiled():
            self._set_compiled(AstDiv(self, other))
            return self
        other = self._get_runtime_other(other)
        self._set_runtime(self._get_runtime() / other)
        return self

    def __floordiv__(self, other):
        raise ArithmeticError('use built-in floor(x) instead')

    def __rfloordiv__(self, other):
        raise ArithmeticError('use built-in floor(x) instead')

    def __ifloordiv__(self, other):
        raise ArithmeticError('use built-in floor(x) instead')

    def __round__(self, other):
        raise ArithmeticError('use built-in round(x) instead')

    def __pow__(self, other):
        raise ArithmeticError('use built-in pow(x) instead')

    def __rpow__(self, other):
        if self.is_compiled():
            return AstPow(other, self)
        other = self._get_runtime_other(other)
        return self._get_runtime() ** other

    def __ipow__(self, other):
        if self.is_compiled():
            self._set_compiled(AstPow(self, other))
            return self
        other = self._get_runtime_other(other)
        self._set_runtime(self._get_runtime() ** other)
        return self

    def __and__(self, other):
        if not self.is_bool():
            raise NotImplementedError
        return super().__and__(other)

    def __rand__(self, other):
        if not self.is_bool():
            raise NotImplementedError
        return super().__rand__(other)

    def __or__(self, other):
        if not self.is_bool():
            raise NotImplementedError
        return super().__or__(other)

    def __ror__(self, other):
        if not self.is_bool():
            raise NotImplementedError
        return super().__ror__(other)


class KspArray(KspVar):
    '''abstract base class for making int str and real KSP arrays
    ref_type is values accepted for sequence input and items assignment
    item_type is single class reference for local object construction
    via __getitem__ and _runtime_iter.
    (local maked by kwarg "local=True", value handles via standart
    kwarg value)
    '''

    def __init__(self, name, name_prefix='', name_postfix='',
                 preserve_name=False, has_init=True,
                 is_local=False, ref_type=None, item_type=None,
                 size=None, seq=None, persist=False, def_val=None):
        super().__init__(name, name_prefix=name_prefix,
                         ref_type=ref_type,
                         name_postfix=name_postfix,
                         preserve_name=preserve_name,
                         has_init=has_init,
                         is_local=is_local,
                         persist=persist)
        if not isinstance(item_type, type):
            raise TypeError('item_type has to be subclass of KspVar')
            if not issubclass(item_type, KspVar):
                raise TypeError(
                    'item_type has to be subclass of KspVar')
        self._item_type = item_type

        self.__pure_name = name
        self.__prefix = name_prefix
        self.__postfix = name_postfix
        self.__init_seq = None
        self._seq = []

        if size is not None:
            if seq:
                if len(seq) > size:
                    raise AttributeError(
                        'size has to be greater or equal length of seq'
                    )
                self._size = len(seq)
            else:
                self._size = 0
            self._init_size = size
            self._seq = [None] * size
        else:
            self._size = 0
            self._init_size = 0
        self._cashed = [None] * self._init_size
        if seq is not None:
            self._seq = self._init_seq(seq)
            self.__init_seq = seq.copy()
        self.__default = def_val

    @property
    def default(self):
        return self.__default

    def _init_seq(self, seq):
        '''makes self._cashed and returns seq
        depends on init arguments'''
        if not isinstance(seq, list):
            raise TypeError('seq has to be instance of list')
        if self._init_size:
            if len(seq) < self._init_size:
                seq.extend([None] * (self._init_size - len(seq)))
        else:
            self._size = len(seq)
            self._cashed = [None] * len(seq)
        return seq.copy()

    def _generate_init(self):
        '''returns declaration line and optional addition assignement
        lines for non-numeric item_types'''
        seq = list()
        out = list()
        if self._init_size:
            size = self._init_size
        else:
            size = self._size
        decl_line = f'declare {self.name()}[{size}]'
        if not self.__init_seq:
            return [decl_line]
        for item in self.__init_seq:
            if isinstance(item, str):
                item = f'"{item}"'
            if isinstance(item, KspVar):
                item = item._get_compiled()
            if isinstance(item, AstBase):
                item = item.expand()
            seq.append(item)
        if issubclass(self._item_type, KspNumeric):
            addit = ':= ('
            for item in seq:
                addit += f'{item}, '
            out = [f'{decl_line} {addit[:-2]})']
            return out
        out.append(decl_line)
        for idx, item in enumerate(seq):
            out.append(f'{self.name()}[{idx}] := {item}')
        return out

    @property
    def item_type(self):
        '''getter for item_type argument'''
        return self._item_type

    def append(self, val):
        '''puts value to the last used key of array, if size permits'''
        if not isinstance(val, self.ref_type):
            raise TypeError(
                f'has to be instance of {self.ref_type}')
        if not self.in_init():
            raise RuntimeError('can not append outside init block')
        if not self._init_size:
            self._seq.append(val)
            self._cashed.append(None)
            self.set_at_idx(self._size, val)
            self._size += 1
            return
        if self._size >= self._init_size:
            raise RuntimeError('can not append. array is full')
        self.set_at_idx(self._size, val)

    def extend(self, seq):
        '''extends array if size permits'''
        if not isinstance(seq, list):
            raise TypeError('has to be list')
        for val in seq:
            self.append(val)

    def __getitem__(self, idx):
        '''returns item_type (KspVar instance) local objects with
        value from squence and name of array index ("array[idx]")
        resource-unefficient. cashes object for later usage, but
        rewrites several methods for keeping index fresh
        For lite usage (just what puted in seq) use _getitem_fast(idx)
        '''
        return self._getitem_full(idx)

    def _getitem_full(self, idx):
        compiled_idx = self._check_idx(idx)
        runtime_idx = self._get_runtime_idx(idx)
        self._check_cashed_item(runtime_idx)
        item = self._cashed[runtime_idx]
        item._set_runtime = \
            lambda val, idx=idx, self=item, arr=self: \
            KspArray._item_set_runtime(self, arr, runtime_idx, val)
        item.name = \
            lambda idx=idx, self=item, arr=self: \
            KspArray._item_name(self, arr, compiled_idx)
        item._get_runtime = \
            lambda idx=idx, self=item, arr=self: \
            KspArray._item_get_runtime(self, arr, runtime_idx)
        return item

    def _getitem_fast(self, idx):
        '''returns value from sequence (even None)
        at idx value (runtime representation)
        '''
        idx = self._get_runtime_idx(idx)
        return self._seq[idx]

    def __setitem__(self, idx, val):
        '''calls self.set_at_idx(idx, val)'''
        self.set_at_idx(idx, val)

    def set_at_idx(self, idx, val):
        '''puts value to the cashed object at idx.
        Or makes one if not exists'''
        if not isinstance(val, self.ref_type):
            raise TypeError(
                f'has to be instance of {self.ref_type}')
        runtime_idx = self._get_runtime_idx(idx)
        if self._size < runtime_idx:
            self._size = runtime_idx
        self._seq[runtime_idx] = self._get_rutime_other(val)
        if self._check_cashed_item(runtime_idx):
            self._getitem_full(idx)
            self._cashed[idx] <<= val

    def _get_runtime_idx(self, idx):
        '''get runtime value from KspIntVar, or return int index'''
        if isinstance(idx, int) and idx < 0:
            idx = self.__len__() + idx
        if isinstance(idx, KspIntVar):
            return idx._get_runtime()
        if isinstance(idx, AstBase):
            return idx.get_value()
        return idx

    def _check_idx(self, idx):
        '''returns index, got from int object, or val property of
        KspIntVar object

        raises TypeError on incorrect index type'''
        if not isinstance(idx, (KspIntVar, int, AstOperator)):
            raise TypeError('has to be int or KspIntVar or AstOperator')
        if isinstance(idx, int) and idx < 0:
            idx = self._size + idx
        if isinstance(idx, KspIntVar):
            idx = idx.val
        if isinstance(idx, AstBase):
            idx = idx.expand()
        return idx

    def _check_cashed_item(self, idx):
        '''returns cashed object from index, or make one.'''
        if self._cashed[idx] is not None:
            return False
        val = self._seq[idx]
        if val is None:
            self._seq[idx] = self.__default
            val = self._seq[idx]
        if not isinstance(val, self.ref_type):
            raise TypeError(
                f'items has to be of type {self.ref_type}; ' +
                f'returned {val} ' +
                f'({type(val)})')
        if isinstance(val, KspVar):
            val = val._get_runtime()
        if isinstance(val, AstBase):
            val = val.get_value()
        item = self._item_type(name=f'{self.name()}[{idx}]',
                               value=val,
                               is_local=True)
        self._cashed[idx] = item
        return True

    def _item_get_compiled(self, arr, idx):
        '''method for overriding cashed item method within new name'''
        return f'{arr.name()}[{idx}]'

    def _item_get_runtime(self, arr, idx):
        '''method for overriding cashed item method within new value'''
        val = arr._seq[idx]
        if isinstance(val, KspVar):
            val = val._get_runtime()
        if isinstance(val, AstBase):
            val = val.get_value()
        return val

    def _item_set_runtime(self, arr, idx, val):
        '''method for overriding cashed item method within new value'''
        arr._seq[idx] = self._get_rutime_other(val)

    def _item_name(self, arr, idx):
        '''method for overriding cashed item method within new name'''
        return f'{arr.name()}[{idx}]'

    def _set_runtime(self, val):
        raise RuntimeError("can't assign to created array")

    def __iter__(self):
        raise NotImplementedError(
            'can not be used in iter.' +
            'use self.iter_runtime or' +
            'self.iter_runtime_fast')

    def __len__(self):
        '''returns init size, if specifyed, or actual size of array.
        for KSP built-in function use built-in func'''
        if self._init_size:
            return self._init_size
        return self._size

    def iter_runtime(self):
        '''returns __getitem__ on each index'''
        for idx in range(self.__len__()):
            yield self.__getitem__(idx)

    def iter_runtime_fast(self):
        '''returns pure objects, stored in seq at each idx'''
        for idx in range(self.__len__()):
            yield self._seq[idx]

    def _generate_executable(self):
        raise NotImplementedError

    def _sort(self, direction):
        for idx in range(len(self._cashed)):
            self._cashed[idx] = None
        self._seq.sort()
        if direction == 0:
            return
        new = list()
        for idx in range(len(self._seq)):
            new.append(self._seq.pop())
        self._seq = new


def get_val(*args):
    out = list()
    for arg in args:
        if isinstance(arg, KspVar):
            out.append(arg.val)
            continue
        out.apend(arg)
    if len(args) == 1:
        return out[0]
    return out


def get_string_repr(*args):
    out = list()
    for arg in args:
        if isinstance(arg, str):
            out.append(arg)
        if isinstance(arg, KspVar):
            out.append(arg._get_compiled())
            continue
        if isinstance(arg, AstBase):
            out.append(arg.expand())
        out.append(f'{arg}')
    if len(args) == 1:
        return out[0]
    return out


def get_runtime(*args):
    out = list()
    for arg in args:
        if isinstance(arg, KspVar):
            out.append(arg._get_runtime())
            continue
        if isinstance(arg, AstBase):
            out.append(arg.get_value())
        out.append(arg)
    if len(args) == 1:
        return out[0]
    return out
