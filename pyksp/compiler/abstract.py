from abc import ABCMeta
from abc import abstractmethod
import hashlib

from typing import List


class SingletonMeta(ABCMeta):
    '''Singleton metaclass'''
    def __init__(cls, *args, **kw):
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = \
                super(SingletonMeta, cls).__call__(*args, **kw)
        return cls.instance


class KspBoolProp:
    '''class property, initialized at False and accepts only bool'''

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
    __in_init = True
    __callback = None
    indents = False
    docs = False

    @staticmethod
    def is_compiled():
        '''check state (changes returns of KSP objects)'''
        return KSP.__is_compiled

    @staticmethod
    def set_callback(obj):
        '''set callback to be counted by built-ins'''
        if obj is None:
            KSP.__callback = obj
            return
        if KSP.__callback is not None:
            raise RuntimeError(f'callback {KSP.__callback} is oened yet')
        KSP.__callback = obj

    @staticmethod
    def callback():
        '''retrieve current callback'''
        return KSP.__callback

    @staticmethod
    def set_compiled(val):
        '''set state (changes returns of KSP objects)'''
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__is_compiled = val

    @staticmethod
    def is_bool():
        '''check state (for usage in if/else select/case blocks)'''
        return KSP.__is_bool

    @staticmethod
    def set_bool(val):
        '''set bool state (for usage in if/else select/case blocks)'''
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__is_bool = val

    @staticmethod
    def in_init(val=None):
        '''val is optional. Within kwarg "val" sets state to it
        without - checks'''
        if val is None:
            return KSP.__in_init
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__in_init = val

    @staticmethod
    def refresh():
        '''sets KSP variables to default'''
        KSP.__is_compiled = False
        KSP.__is_bool = False
        KSP.__in_init = True
        KSP.indents = False
        KSP.docs = False


class INameLocal(KSP):
    '''Object name interface.
    Example:
    class Test2:

        def __init__(self, name='myname'):
            self.name = INameLocal(name)
    prefix and postfix used in childs for preserving order of strings
    '''

    script_prefix = ''

    def __init__(self, name, prefix='', postfix=''):
        self._name = name
        self._prefix = prefix
        self._postfix = postfix

    def __call__(self):
        return self._prefix + IName.script_prefix +\
            self._name + self._postfix

    @staticmethod
    def refresh():
        IName.script_prefix = ''


class IName(INameLocal):
    '''name can be compacted by default. For preserving use
    preserve=True
    prefix and postfix are always preserved and placed at sides.
    '''

    __is_compact = False
    __names: List[str] = list()
    __scope: List[str] = ['']

    @staticmethod
    def is_compact():
        '''check if names are hashed'''
        return IName.__is_compact

    @staticmethod
    def set_compact(val):
        '''at True hashes names to 5-letter'''
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        IName.__is_compact = val

    def __init__(self, name, prefix='', postfix='',
                 preserve=False):
        # print(IName.__scope)
        name = IName.__scope[-1] + name
        self._preserve = preserve
        self._full = name
        if not preserve and self.is_compact() is True:
            name = self.get_compact_name(name)
        else:
            name = name
        if name in IName.__names:
            raise NameError(f'name "{name}" exists')
        IName.__names.append(name)
        super().__init__(name=name,
                         prefix=prefix, postfix=postfix)

    @staticmethod
    def get_compact_name(name):
        '''hashing func'''
        symbols = 'abcdefghijklmnopqrstuvwxyz012345'
        hash = hashlib.new('sha1')
        hash.update(name.encode('utf-8'))
        compact = ''.join((symbols[ch & 0x1F] for ch
                           in hash.digest()[:5]))
        return compact

    @staticmethod
    def scope(name: str=''):
        if not name:
            IName.__scope.pop()
            return
        IName.__scope.append(name)

    @property
    def full(self):
        return self._full

    @staticmethod
    def refresh():
        INameLocal.refresh()
        IName.__names = list()
        IName.__is_compact = False


class KspObject(KSP):
    '''Base abstract class for all objects can be
    translated to code'''

    comments = KspBoolProp()
    _instances: List['KspObject'] = list()

    @property
    def has_init(self):
        '''True if has to return init block'''
        return self._has_init

    @property
    def is_local(self):
        '''True if has not return init and executable block'''
        return self._is_local

    @property
    def has_executable(self):
        '''True if has to return executable block'''
        return self._has_executable

    @staticmethod
    def instances():
        return KspObject._instances

    @abstractmethod
    def __init__(self, name, name_prefix='', name_postfix='',
                 preserve_name=False,
                 has_init=True, is_local=False, has_executable=False):
        self._is_local = is_local
        if is_local:
            if has_init:
                raise AttributeError('can not have init within local')
            if has_executable:
                raise AttributeError('can not have executable code' +
                                     ' within local')
            if preserve_name:
                raise AttributeError('local name is already preserved')
            self.name = INameLocal(name, name_prefix, name_postfix)
        else:
            self.name = IName(name, name_prefix, name_postfix,
                              preserve_name)
        self._has_init = has_init
        self._has_executable = has_executable
        KspObject._instances.append(self)

    @abstractmethod
    def _generate_init(self):
        pass

    @abstractmethod
    def _generate_executable(self):
        pass

    @staticmethod
    def generate_all_inits():
        '''return init lines for every instance marked to
        generate init block'''
        out = list()
        for inst in KspObject.instances():
            if not inst._has_init:
                continue
            inst_init = inst._generate_init()
            if inst_init is None:
                continue
            if isinstance(inst_init, str):
                raise TypeError('can not add string')
            out.extend(inst_init)
        return out

    @staticmethod
    def generate_all_executables():
        '''return init lines for every instance marked to
        generate executable block'''
        out = list()
        for inst in KspObject.instances():
            if not inst._has_executable:
                continue
            inst_exec = inst._generate_executable()
            if inst_exec is None:
                continue
            if isinstance(inst_exec, str):
                raise TypeError('can not add string')
            out.extend(inst_exec)
        return out

    @staticmethod
    def refresh():
        '''clear all instances'''
        KspObject._instances = list()


class Output(metaclass=SingletonMeta):
    '''Singleton interface for managing pure code'''

    class IsSetError(Exception):
        def __init__(self, extra=''):
            super().__init__('Output is set yet. ' + extra)

    class IndentError(Exception):
        def __init__(self, extra=''):
            super().__init__(extra)

    blocked = KspBoolProp()

    def indent(self):
        """increase indentation level to be used within compilation"""
        # if self.blocked:
        #     return
        # self.put('{indented. indent level is %s}' % (self.__indent + 1))
        self.__indent += 1

    def unindent(self):
        """increase indentation level to be used within compilation"""
        # if self.blocked:
        #     return
        self.__indent -= 1
        # self.put('{unindented. indent level is %s}' % self.__indent)
        if self.__indent < 0:
            raise self.IndentError('indent level below 0')

    def __init__(self):
        self.__default = list()
        self.callable_on_put = None
        self.exception_on_put = None
        self.__output = self.__default
        self.__indent = int()

    def set(self, obj):
        '''set list for code from internal to external
        (callback body, for example)
        raises self.IsSetError if already set
        (e.g. can output only to top level)'''
        if self.__output is not self.__default:
            raise self.IsSetError
        self.__output = obj

    def release(self):
        '''set output to internal list'''
        self.__output = self.__default

    def get(self):
        '''get all items of current list'''
        return self.__output

    def put(self, data):
        '''put item in list and perform actions based on flags:
        exception_on_put - raises exception, if not None
        callable_on_put - executes callable once at put
        and set it to None
        '''
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
        if KSP.indents is not False:
            data = self.__indent * KSP.indents * ' ' + data
        self.__output.append(data)

    def pop(self):
        '''pop the last index from list'''
        return self.__output.pop().strip()

    def refresh(self):
        '''erase all data from internal list and set defaults'''
        self.__default = list()
        self.__output = self.__default
        self.blocked = False
        self.exception_on_put = None
        self.callable_on_put = None


if __name__ == '__main__':
    a = Output()
