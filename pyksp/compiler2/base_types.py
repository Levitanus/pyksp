from abc import abstractmethod

from abstract import KspObject
from abstract import KSP
from abstract import Output


class AstBase(KSP):

    @abstractmethod
    def expand(self):
        pass


class AstAssign(AstBase):

    def __init__(self, to_arg, from_arg):
        if isinstance(to_arg, KspVar):
            self._to_arg = to_arg.val
        else:
            raise TypeError(f'can assign only to instance of {KspVar}')
        if callable(from_arg):
            self._from_arg = from_arg()
        if isinstance(from_arg, str):
            self._from_arg = from_arg
        elif isinstance(from_arg, AstBase):
            self._from_arg = from_arg.expand()
        elif isinstance(from_arg, KspVar):
            self._from_arg = from_arg.val
        else:
            raise TypeError('can assign only instances of: %s' % (
                (KspVar, str, AstBase)
            ))

    def expand(self):
        super().expand()
        return f'{self._to_arg} := {self._from_arg}'


class AstAddString(AstBase):

    def __init__(self, arg1, arg2):
        args = [arg1, arg2]
        self._args = list()
        for arg in args:
            if callable(arg):
                arg = arg()
            if isinstance(arg, str):
                self.args.append(f'"arg"')
                continue
            if isinstance(arg, AstBase):
                self._args.append(arg.expand())
                continue
            if isinstance(arg, KspVar):
                self._args.append(f'{arg.val}')
                continue
            raise NotImplementedError('maybe something has to be added ' +
                                      f'to {AstAddString}?')

    def expand(self):
        super().expand()
        return f'{self._args[0]} & {self._args[1]}'


class KspVar(KspObject):

    def __init__(self, name, name_prefix='',
                 preserve_name=False,
                 has_init=True, is_local=False):
        super().__init__(name, name_prefix=name_prefix,
                         preserve_name=preserve_name,
                         has_init=has_init, is_local=is_local,
                         has_executable=False)

    def _set_compiled(self, val):
        Output().put(AstAssign(self, val).expand)

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
        pass

    def __rlshift__(self, other):
        pass

    @property
    @abstractmethod
    def val(self):
        pass


class KspStrVar(KspVar):

    def __add__(self, other):
        if self.is_compiled:
            return self._add_compiled(self, other)
        return self._add_runtime(self, other)

    def __radd__(self, other):
        if self.is_compiled:
            return self._add_compiled(other, self)
        return self._add_runtime(other, self)

    def __iadd__(self, other):
        if self.is_compiled:
            add = self.__add_compiled(other, self)
            self._set_compiled(add)
            return self
        add = self.__add_runtime(other, self)
        self._set_runtime(add)
        return self

    def _add_compiled(self, arg1, arg2):
        return AstAddString(arg1, arg2)

    def _add_runtime(self, arg1, arg2):
        if arg1 is self:
            arg1 = self.val
            arg2 = self.__check_add_runtime_str(arg2)

    def __check_add_runtime_str(self, other):
        if isinstance(other, KspVar):
            return f'{other.val}'
        raise TypeError('has to be str')
