'''provides classes, representing data structures of KSP
variables – kInt, kStr, kReal
arrays – kArrInt, kArrStr, kArrReal

init arguments for variables:
    (value=<default>, name=None, preserve=False,
    is_local=False, persist=False)

    value is value, stored in variable
    name is representation in compiled code
    if preserve is True, name will not be compacted
    is_local has not to be used, used for handling arrays items
    if persist is True, line "make_persistent(<name>)" will be added
        after init declaration. The same line will be added if function
        var.read() has been called

kVar – universal constructor for native objects. See doc for details.

API syntax:
variables:
    var <<= value # assignement
    value <<= var # assignes var.val to value
    var.val #get value of var
    var.read() # read persistent value (works only inside Kontakt)
    kInt().inc(); kInt().dec() # API to KSP function inc and dec

arrays:
    arr <<= val # error
    arr[idx] # returns k<Var> of arr type
        increases size of array is it is less then idx (affects append
        and extend methods)

    arr.append(value) # if called outside of callbacks or functions
        increases size of array and puts value into it.
        raises IndexError is called from callback or array with fixed
        size is full.
    arr.extend(list(values)) # the same for list
'''

from base_types import KspIntVar
from base_types import KspStrVar
from base_types import KspRealVar
from base_types import KspArray

from base_types import AstOperator
from base_types import AstAddString

from abstract import Output
from abstract import SingletonMeta


class kInt(KspIntVar):
    '''See module doc'''
    warning_types = (KspStrVar, KspRealVar, str, float)
    names_count = 0

    def __init__(self, value=0, name=None, preserve=False,
                 is_local=False, persist=False):
        if is_local:
            has_init = False
        else:
            has_init = True
        if not name:
            name = f'kInt{kInt.names_count}'
            kInt.names_count += 1
        super().__init__(name, value=value,
                         ref_type=(int, KspIntVar, AstOperator),
                         name_prefix='$', name_postfix='',
                         preserve_name=preserve,
                         has_init=has_init,
                         is_local=is_local,
                         persist=persist)
        self.__init_val = value

    def _generate_init(self):
        out = list()
        asgn = ''
        if self.__init_val:
            asgn = f' := {self.__init_val}'
        out.append(f'declare {self.name()}{asgn}')
        if self._persistent or self._read:
            out.append(f'make_persistent({self.name()})')
        return out

    def _get_compiled(self):
        return self.name()

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        self._value = other

    def inc(self):
        if self.is_compiled():
            Output().put(f'inc({self.name()})')
        self._value += 1

    def dec(self):
        if self.is_compiled():
            Output().put(f'dec({self.name()})')
        self._value -= 1


class kReal(KspRealVar):
    '''See module doc'''
    warning_types = (KspStrVar, KspIntVar, str, int)
    names_count = 0

    def __init__(self, value=0.0, name=None, preserve=False,
                 is_local=False, persist=False):
        if is_local:
            has_init = False
        else:
            has_init = True
        if not name:
            name = f'kReal{kReal.names_count}'
            kReal.names_count += 1

        super().__init__(name, value=value,
                         ref_type=(float, KspRealVar, AstOperator),
                         name_prefix='~', name_postfix='',
                         preserve_name=preserve,
                         has_init=has_init,
                         is_local=is_local,
                         persist=persist)
        self.__init_val = value

    def _generate_init(self):
        out = list()
        asgn = ''
        if self.__init_val:
            asgn = f' := {self.__init_val}'
        out.append(f'declare {self.name()}{asgn}')
        if self._persistent or self._read:
            out.append(f'make_persistent({self.name()})')
        return out

    def _get_compiled(self):
        return self.name()

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        self._value = other


class kStr(KspStrVar):
    '''See module doc'''
    warning_types = (KspIntVar, KspRealVar, int, float)
    names_count = 0

    def __init__(self, value='', name=None, preserve=False,
                 is_local=False, persist=False):
        if is_local:
            has_init = False
        else:
            has_init = True
        if not name:
            name = f'kStr{kStr.names_count}'
            kStr.names_count += 1

        super().__init__(name, value=value,
                         ref_type=(str, KspStrVar, AstAddString,
                                   KspIntVar, KspRealVar),
                         name_prefix='@', name_postfix='',
                         preserve_name=preserve,
                         has_init=has_init,
                         is_local=is_local,
                         persist=persist)
        self.__init_val = value

    def _generate_init(self):
        out = list()
        out.append(f'declare {self.name()}')
        if self.__init_val:
            if isinstance(self.__init_val, str):
                self.__init_val = f'"{self.__init_val}"'
            out.append(f'{self.name()} := {self.__init_val}')
        if self._persistent or self._read:
            out.append(f'make_persistent({self.name()})')
        return out

    def _get_compiled(self):
        return self.name()

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        self._value = other


class kArrInt(KspArray):
    '''See module doc'''
    names_count = 0

    def __init__(self, sequence=None,
                 name=None,
                 size=None,
                 preserve=False,
                 persist=False,
                 is_local=False):
        if is_local:
            has_init = False
        else:
            has_init = True
        if not name:
            name = f'kArrInt{kArrInt.names_count}'
            kArrInt.names_count += 1
        super().__init__(name, name_prefix='%',
                         name_postfix='',
                         preserve_name=preserve,
                         has_init=has_init,
                         is_local=is_local,
                         ref_type=(int, KspIntVar, AstOperator),
                         item_type=kInt,
                         size=size,
                         seq=sequence,
                         def_val=0)

    def _get_compiled(self):
        return self.name()

    def _get_runtime(self):
        return self._seq

    def _generate_init(self):
        out = super()._generate_init()
        if self._persistent or self._read:
            out.append(f'make_persistent({self.name()})')
        return out


class kArrReal(KspArray):
    '''See module doc'''
    names_count = 0

    def __init__(self, sequence=None,
                 name=None,
                 size=None,
                 preserve=False,
                 persist=False,
                 is_local=False):
        if is_local:
            has_init = False
        else:
            has_init = True
        if not name:
            name = f'kArrReal{kArrReal.names_count}'
            kArrReal.names_count += 1
        super().__init__(name, name_prefix='?',
                         name_postfix='',
                         preserve_name=preserve,
                         has_init=has_init,
                         is_local=is_local,
                         ref_type=(float, KspRealVar, AstOperator),
                         item_type=kReal,
                         size=size,
                         seq=sequence,
                         def_val=0.0)

    def _get_compiled(self):
        return self.name()

    def _get_runtime(self):
        return self._seq

    def _generate_init(self):
        out = super()._generate_init()
        if self._persistent or self._read:
            out.append(f'make_persistent({self.name()})')
        return out


class kArrStr(KspArray):
    '''See module doc'''
    names_count = 0

    def __init__(self, sequence=None,
                 name=None,
                 size=None,
                 preserve=False,
                 persist=False,
                 is_local=False):
        if is_local:
            has_init = False
        else:
            has_init = True
        if not name:
            name = f'kArrStr{kArrStr.names_count}'
            kArrStr.names_count += 1
        super().__init__(name, name_prefix='!',
                         name_postfix='',
                         preserve_name=preserve,
                         has_init=has_init,
                         is_local=is_local,
                         ref_type=(str, KspStrVar, AstOperator),
                         item_type=kStr,
                         size=size,
                         seq=sequence,
                         def_val='')

    def _get_compiled(self):
        return self.name()

    def _get_runtime(self):
        return self._seq

    def _generate_init(self):
        out = super()._generate_init()
        if self._persistent or self._read:
            out.append(f'make_persistent({self.name()})')
        return out


def refresh_names_count():
    kInt.names_count = 0
    kStr.names_count = 0
    kReal.names_count = 0
    kArrInt.names_count = 0
    kArrStr.names_count = 0
    kArrReal.names_count = 0


class kVar:
    '''returns KSP native var at construction or with assignement via
    <<= operator.
    arguments: (value=None, name=None, size=None,
                preserve=False, persist=False)
        if value, ready object is returned
        if not, object has to be initialized via <<= operator

    if init_value is:
        int, kInt -> kInt
        str, kStr -> kStr
        float, kReal -> kReal
        list -> kArr, depends on first item type
    '''
    names_count = 0

    def __new__(cls, value=None, name=None, size=None,
                preserve=False, persist=False):
        if not name:
            name = f'kVar{kVar.names_count}'
            kVar.names_count += 1
        if not value:
            obj = super(kVar, cls).__new__(cls)
            d = obj.__dict__
            d['name'] = name
            d['size'] = size
            d['preserve'] = preserve
            d['persist'] = persist
            return obj
        if isinstance(value, (int, KspIntVar)):
            return kInt(value=value, name=name,
                        preserve=preserve, persist=persist)
        if isinstance(value, (str, KspStrVar)):
            return kStr(value=value, name=name,
                        preserve=preserve, persist=persist)
        if isinstance(value, (float, KspRealVar)):
            return kReal(value=value, name=name,
                         preserve=preserve, persist=persist)
        if isinstance(value, list):
            if isinstance(value[0], (int, KspIntVar)):
                return kArrInt(value=value, name=name,
                               preserve=preserve, persist=persist,
                               size=size)
            if isinstance(value[0], (str, KspStrVar)):
                return kArrStr(value=value, name=name,
                               preserve=preserve, persist=persist,
                               size=size)
            if isinstance(value[0], (float, KspRealVar)):
                return kArrReal(value=value, name=name,
                                preserve=preserve, persist=persist,
                                size=size)
        raise TypeError('can be initialized only with:%s' %
                        (int, str, float, kInt, kStr, kReal, list))

    def __ilshift__(self, value):
        if isinstance(value, (int, KspIntVar)):
            if self.size:
                raise TypeError('for arrays initialization use list')
            return kInt(value=value, name=self.name,
                        preserve=self.preserve, persist=self.persist)
        if isinstance(value, (str, KspStrVar)):
            if self.size:
                raise TypeError('for arrays initialization use list')
            return kStr(value=value, name=self.name,
                        preserve=self.preserve, persist=self.persist)
        if isinstance(value, (float, KspRealVar)):
            if self.size:
                raise TypeError('for arrays initialization use list')
            return kReal(value=value, name=self.name,
                         preserve=self.preserve, persist=self.persist)
        if isinstance(value, list):
            if isinstance(value[0], (int, KspIntVar)):
                return kArrInt(sequence=value, name=self.name,
                               preserve=self.preserve,
                               persist=self.persist,
                               size=self.size)
            if isinstance(value[0], (str, KspStrVar)):
                return kArrStr(sequence=value, name=self.name,
                               preserve=self.preserve,
                               persist=self.persist,
                               size=self.size)
            if isinstance(value[0], (float, KspRealVar)):
                return kArrReal(sequence=value, name=self.name,
                                preserve=self.preserve,
                                persist=self.persist,
                                size=self.size)
        raise TypeError('can be initialized only with:%s' %
                        (int, str, float, kInt, kStr, kReal, list))


class kNone(kInt, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__(value=-1, name='None',
                         preserve=False, is_local=True)

    def _get_compiled(self):
        return self._value

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        raise NotImplementedError

    def _set_compiled(self, other):
        raise NotImplementedError

    def inc(self):
        raise NotImplementedError

    def dec(self):
        raise NotImplementedError


class kFalse(kInt):

    def __init__(self):
        super().__init__(value=0, name='None',
                         preserve=False, is_local=True)

    def _get_compiled(self):
        return self._value

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        raise NotImplementedError

    def _set_compiled(self, other):
        raise NotImplementedError

    def inc(self):
        raise NotImplementedError

    def dec(self):
        raise NotImplementedError


class kTrue(kInt):

    def __init__(self):
        super().__init__(value=1, name='None',
                         preserve=False, is_local=True)

    def _get_compiled(self):
        return self._value

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        raise NotImplementedError

    def _set_compiled(self, other):
        raise NotImplementedError

    def inc(self):
        raise NotImplementedError

    def dec(self):
        raise NotImplementedError

    def __eq__(self, other):
        return 0 < other
