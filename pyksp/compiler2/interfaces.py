import hashlib


class IOutput:
    '''
    Singletone Interface for centralized comunication
    between objects.
    Originally designed for AST collection, but can be
    instantiated by:
        INewOutput = IOutput
    and be used with other purpose
    '''

    _default = list()
    _output = _default
    _blocked = False
    _exception = None
    _callable_on_put = None

    def __new__(cls):
        return IOutput

    class IsSetError(Exception):
        pass

    @staticmethod
    def _raise_set_err():
        msg = "Output can't be set now. "\
            "If You want to have set"\
            " functionality in some cases, use try-except block"
        raise IOutput.IsSetError(msg)

    @staticmethod
    def set(output):
        '''
        redirect output of all put(data) calls to another list
        have to be released by release() method after all
        '''
        if IOutput._output is not IOutput._default:
            IOutput._raise_set_err()
        IOutput._output = output

    @staticmethod
    def get():
        '''
        get result list
        '''
        return IOutput._output

    @staticmethod
    def put(data):
        '''
        put data to current output list
        '''
        if IOutput._exception:
            raise IOutput._exception
        if IOutput._callable_on_put:
            IOutput._callable_on_put()
            IOutput._callable_on_put = None
        if not IOutput._blocked:
            IOutput._output.append(data)

    @staticmethod
    def pop():
        return IOutput._output.pop()

    @staticmethod
    def exception_on_put(exc):
        IOutput._exception = exc

    @staticmethod
    def callable_on_put(obj):
        IOutput._callable_on_put = obj

    @staticmethod
    def get_callable_on_put():
        return IOutput._callable_on_put

    @staticmethod
    def release():
        '''
        set output list to default
        '''
        IOutput._output = IOutput._default

    @staticmethod
    def lock():
        IOutput._blocked = True

    @staticmethod
    def unlock():
        IOutput._blocked = False

    @staticmethod
    def refresh():
        '''
        Method for resetting interface variables to defaults.
        Used for clearing data with multiple scrits compilation.
        '''
        IOutput._default.clear()
        IOutput.release()


class IName:
    '''class for handling names.
    With compact option enabled hashes long names to
    5-letter names, handling a simple obfuscation.
    To keep name untouched by compacting initialize
    instance with:
        IName(full_name, preserve_name=True)
    '''

    __prefix = ''
    __shuffle = 'key'
    compact = False
    __names = list()

    def __init__(self, full_name: str, preserve_name: bool=False):
        if not isinstance(full_name, str):
            raise TypeError('name has to be string')
        if not isinstance(preserve_name, bool):
            raise TypeError('preserve_name has to be bool')
        # print(preserve_name)
        if full_name in IName.__names:
            raise NameError('Name %s exists. Try enother, '
                            'or add scope to it within __module__'
                            % full_name)
        self._name = full_name
        self._preserve = preserve_name
        self.idx = len(IName.__names)
        IName.__names.append(self._name)
        self.prefix: str = ''

    def __call__(self, full=False):
        if full:
            return self.get_full_name()
        if IName.compact:
            return self.get_compact_name()
        return self.get_full_name()

    def get_full_name(self):
        return self.prefix + IName.__prefix + self._name

    def get_compact_name(self):
        if self._preserve:
            return self.get_full_name()
        name = self._name
        symbols = 'abcdefghijklmnopqrstuvwxyz012345'
        hash = hashlib.new('sha1')
        hash.update(name.encode('utf-8'))
        compact = ''.join((symbols[ch & 0x1F] for ch
                           in hash.digest()[:5]))
        return self.prefix + compact

    @staticmethod
    def refresh():
        IName.__prefix = ''
        IName.__shuffle = 'key'
        IName.compact = False
        IName.__names = list()


class INameLocal(IName):
    '''class for handling names.
    With compact option enabled hashes long names to
    5-letter names, handling a simple obfuscation.
    To keep name untouched by compacting initialize
    instance with:
        IName(full_name, preserve_name=True)
    '''

    def __init__(self, full_name: str):
        if not isinstance(full_name, str):
            raise TypeError('name has to be string')
        self._name = full_name
        self._preserve = False
        self.prefix: str = ''


if __name__ == '__main__':
    name = IName('var')
    IName.refresh()
    name = IName('var')
    print(name())
