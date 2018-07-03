from abc import ABCMeta
from abc import abstractmethod

# from interfaces import ICompactName
from interfaces import IName


class KSP(metaclass=ABCMeta):

    __test_env = False
    __is_bool = False

    @staticmethod
    def is_bool():
        return KSP.__is_bool

    @staticmethod
    def toggle_bool(state: bool):
        if not isinstance(state, bool):
            raise TypeError(f'accepts bool, passed {type(state)}')
        KSP.__is_bool = state

    def is_under_test(self=None) -> bool:
        '''if test enviropment has be turen on
        return True
        '''
        return KSP.__test_env

    @staticmethod
    def toggle_test_state(value: bool = None):
        '''toggles behaviouur to test. Has to be set to
        True via setting of the test enviropment'''
        if value is not None:
            KSP.__test_env = value
            return value
        if KSP.__test_env is True:
            KSP.__test_env = False
            return
        KSP.__test_env = True
        return True


class KspObject(KSP):
    '''Base class for all objects, appears in code.
    Keeps all instances inside, has to be re-initialized
    via KspObject.refresh() method at every script compilation
    or code generation test.
    '''

    comments = False
    __count = 0
    __instances = list()

    def __init__(self, full_name, preserve_name=False):
        self.name = IName(full_name, preserve_name)
        self.__instance_idx = KspObject.__count
        KspObject.__instances.append(self)

    @staticmethod
    def generate_init():
        init_lines = list()
        for instance in KspObject.__instances:
            init_lines.extend(instance._generate_init())
        return init_lines

    @staticmethod
    def generate_executable():
        return []

    @staticmethod
    def refresh():
        KspObject.comments = False
        KspObject.__count = 0
        KspObject.__instances = list()


def Singleton(class_):
    _instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in _instances:
            obj = class_(*args, **kwargs)
            _instances[class_] = obj
        return _instances[class_]
    return getinstance
