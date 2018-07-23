from abc import ABCMeta
from abc import abstractmethod
import hashlib


class SingletonMeta(type):
    def __init__(cls, *args, **kw):
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(SingletonMeta, cls).__call__(*args, **kw)
        return cls.instance


class KspBoolProp:

    def __init__(self):
        self.__val = False

    def __get__(self, obj, cls):
        return self.__val

    def __set__(self, obj, val):
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        self.__val = val

    def __delete__(self):
        raise RuntimeError('can not be deleted')


class KSP(metaclass=ABCMeta):
    '''Base abstract class for all compiler classes'''
    __is_compiled = False
    __is_bool = False

    @staticmethod
    def is_compiled():
        return KSP.__is_compiled

    @staticmethod
    def set_compiled(val):
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__is_compiled = val

    @staticmethod
    def is_bool():
        return KSP.__is_bool

    @staticmethod
    def set_bool(val):
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__is_bool = val


class INameLocal(KSP):
    '''Object name interface. Requires instance._name attribute
    Example:
    class Test2:

        name = Name('$')

        def __init__(self, name='my name'):
            self._name = name
    '''

    script_prefix = ''

    def __init__(self, name, prefix=''):
        self._name = name
        self._prefix = prefix

    def __call__(self):
        return self._prefix + IName.script_prefix + self._name

    @staticmethod
    # @abstractmethod
    def refresh():
        IName.script_prefix = ''


class IName(INameLocal):

    __is_compact = False
    __names = list()

    @staticmethod
    def is_compact():
        return IName.__is_compact

    @staticmethod
    def set_compact(val):
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        IName.__is_compact = val

    def __init__(self, name, prefix='', preserve=False):
        self._preserve = preserve
        if preserve is False and self.is_compact() is True:
            name = self.get_compact_name(name)
        else:
            name = name
        if name in IName.__names:
            raise NameError('name exists')
        IName.__names.append(name)
        super().__init__(name=name, prefix=prefix)

    @staticmethod
    def get_compact_name(name):
        symbols = 'abcdefghijklmnopqrstuvwxyz012345'
        hash = hashlib.new('sha1')
        hash.update(name.encode('utf-8'))
        compact = ''.join((symbols[ch & 0x1F] for ch
                           in hash.digest()[:5]))
        return compact

    @staticmethod
    def refresh():
        INameLocal.refresh()
        IName.__names = list()


class KspObject(KSP):
    '''Base abstract class for all objects can be
    translated to code'''

    comments = KspBoolProp()
    __instances = list()

    @property
    def has_init(self):
        return self._has_init

    @property
    def is_local(self):
        return self._is_local

    @property
    def has_executable(self):
        return self._has_executable

    @property
    def name(self):
        return self._name

    @abstractmethod
    def __init__(self, name, name_prefix='', preserve_name=False,
                 has_init=True, is_local=False, has_executable=False):
        if is_local:
            if has_init:
                raise AttributeError('can not have init within local')
            if has_executable:
                raise AttributeError('can not have executable code' +
                                     ' within local')
            if preserve_name:
                raise AttributeError('local name is already preserved')
            self._name = INameLocal(name, name_prefix)
        else:
            self._name = IName(name, name_prefix, preserve_name)
        self.__has_init = has_init
        self.__has_executable = has_executable
        KspObject.__instances.append(self)

    @abstractmethod
    def generate_init(self):
        pass

    @abstractmethod
    def generate_executable(self):
        pass

    @staticmethod
    def generate_all_inits():
        out = list()
        for inst in KspObject.__instances:
            if not inst.__has_init:
                continue
            inst_init = inst.generate_init()
            if inst_init is None:
                continue
            if isinstance(inst_init, str):
                raise TypeError('can not add string')
            out.extend(inst_init)
        return out

    @staticmethod
    def generate_all_executables():
        out = list()
        for inst in KspObject.__instances:
            if not inst.__has_executable:
                continue
            inst_exec = inst.generate_executable()
            if inst_exec is None:
                continue
            if isinstance(inst_exec, str):
                raise TypeError('can not add string')
            out.extend(inst_exec)
        return out

    @staticmethod
    def refresh():
        KspObject.__instances = list()


class Output(metaclass=SingletonMeta):

    class IsSetError(Exception):
        def __init__(self, extra=''):
            super().__init__('Output is set yet. ' + extra)

    blocked = KspBoolProp()

    def __init__(self):
        self.__default = list()
        self.callable_on_put = None
        self.exception_on_put = None
        self.__output = self.__default

    def set(self, obj):
        if self.__output is not self.__default:
            raise self.IsSetError
        self.__output = obj

    def release(self):
        self.__output = self.__default

    def get(self):
        return self.__output

    def put(self, data):
        if self.exception_on_put:
            raise self.exception_on_put
        if self.callable_on_put:
            self.callable_on_put()
            self.callable_on_put = None
        if self.blocked:
            return
        if isinstance(data, list):
            self.__output.extend(data)
            return
        self.__output.append(data)

    def pop(self):
        return self.__output.pop()

    def refresh(self):
        self.__default = list()
        self.__output = self.__default
        self.blocked = False
        self.exception_on_put = None
        self.callable_on_put = None


if __name__ == '__main__':
    a = Output()
