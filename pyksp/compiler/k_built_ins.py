# from abc import abstractmethod
# from functools import wraps
from functools import partialmethod
import functools
from inspect import signature
from collections import OrderedDict
# import re

from typing import Tuple
from typing import Union

import math
import random

# from .abstract import KspObject
from .abstract import Output
from .abstract import KSP
# from .abstract import SingletonMeta

from .base_types import KspVar
from .base_types import KspArray
from .base_types import KspIntVar
from .base_types import KspStrVar
from .base_types import KspRealVar
from .base_types import AstBase

from .native_types import kInt
from .native_types import kArrInt
from .native_types import kStr
from .native_types import kReal
from .native_types import kArrReal
from .native_types import kNone

all_callbacks = object()


def get_runtime_val(val):
    if hasattr(val, '_get_runtime'):
        return val._get_runtime()
    if hasattr(val, 'get_value'):
        return val.get_value()
    return val


def get_compiled(val):
    if hasattr(val, '_get_compiled'):
        return val._get_compiled()
    if hasattr(val, 'expand'):
        return val.expand()
    return val


def _all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _all_subclasses(c)]
    )


class Callback(KSP):

    __callbacks = list()
    __current = None
    __id = int()

    def __init__(
        self,
        header: str,
        cb_type: 'bCallbackVar',
        built_in_vars: Tuple[str]
    ):
        Callback.__callbacks.append(self)
        self._header = header
        self.__lines = list()
        self._type = cb_type
        self.__functions = set()
        self.__bvars = dict()
        for var in built_in_vars:
            self.__bvars[var] = -1

    def add_function(self, function):
        self.__functions.add(function)

    def open(self):
        Callback.__id += 1
        NI_CALLBACK_ID.set_value(Callback.__id)
        NI_CALLBACK_TYPE.set_value(self._type)
        # Output().indent()
        Output().set(self.__lines)
        self.set_callback(self)

    def close(self, keep_type=None):
        if keep_type:
            NI_CALLBACK_TYPE.set_value(self._type)
        Output().release()
        self.set_callback(None)
        # Output().unindent()

    def generate_body(self):
        if not self.__functions:
            return []
        out = list()
        out.append(f'on {self._header}')
        Output().indent()
        # out.extend(self.__lines)
        self.__lines.clear()
        self.open()
        for func in self.__functions:
            sig = signature(func)
            if not sig.parameters:
                func()
            else:
                try:
                    print(sig.parameters)
                    obj = sig.parameters['self']
                    func(obj)
                except AttributeError as e:
                    raise RuntimeError(
                        'probably, used as decorator of class method.' +
                        ' Invoke as function with method name as' +
                        ' argument. Example: init(self.method)' +
                        'or use as decorator with no arguments passed\n'
                        + f'original exception: {e}'
                    )
                except KeyError:
                    func()
        out.extend(self.__lines)
        self.close()
        Output().unindent()
        out.append(f'end on')
        return out

    @staticmethod
    def get_all_bodies():
        out = list()
        for cb in Callback.__callbacks:
            if cb is InitCallback:
                continue
            out.extend(cb.generate_body())
        return out

    @staticmethod
    def refresh():
        for cb in Callback.__callbacks:
            cb._refresh()
        KSP.set_callback(None)

    def _refresh(self):
        self.__lines.clear()
        self.__lines = list()
        self.__functions = set()
        self.__bvars = dict()


class InitCallbackCl(Callback):
    def open(self):
        super().open()
        KSP.in_init(True)

    def close(self):
        super().close()
        KSP.in_init(False)


class Control(KSP):
    def __init__(self, control: KspVar):
        self.lines = list()
        self.control = control


class UiControlCallbackCl(Callback):
    def __init__(self, cb_type):
        super().__init__('ui_control', cb_type, ('control', ))
        self.__controls = dict()

    def open(self, control: KspVar = None):
        super().open()
        if control and control.name() in self.__controls.keys():
            raise RuntimeError(
                f'callback of {control.name()} has' + ' been set yet'
            )
        if not control:
            control = self._last_control
        else:
            self.__controls[control.name()] = Control(control)
        Output().release()
        # Output().indent()
        Output().set(self.__controls[control.name()].lines)
        self._last_control = control

    def generate_body(self):
        if not self.__controls:
            return []
        out = list()
        for name, control in self.__controls.items():
            out.append(f'on {self._header}({name})')
            out.extend(control.lines)
            out.append(f'end on')
        return out

    def _refresh(self):
        super()._refresh()
        self.__controls = dict()


class FunctionCallbackCl(Callback):
    def __init__(self):
        super().__init__('function', -1, tuple())
        self.__root = None
        self.__levels = 0

    def open(self):
        if self.callback() is None:
            self.__levels = 1
            # Output().indent()
            return self.set_callback(self)
        if self.callback() is self:
            self.__levels += 1
            return
        self.__root = self.callback()
        self.__root.close(keep_type=True)
        # Output().indent()
        self.set_callback(self)

    def close(self):
        if self.callback() is self:
            self.__levels -= 1
            if self.__levels <= 0:
                self.__levels = 0
                # Output().unindent()
                self.set_callback(None)
                if self.__root:
                    self.__root.open()
                    self.__root = None
            return
        # Output().unindent()
        self.set_callback(None)
        self.__root.open()
        self.__root = None
        return

    def generate_body(self):
        return []


class BuiltIn(KSP):

    _id_count = int()
    _instances = list()

    def __init__(self, callbacks=all_callbacks):
        self._id = BuiltIn._id_count
        BuiltIn._instances.append(self)
        BuiltIn._id_count += 1
        self._callbacks = callbacks
        # self.__def_val = def_val

    @property
    def id(self):
        # if self.is_compiled():
        #     return self.name()
        return self._id

    @staticmethod
    def get_by_id(idx):
        if hasattr(idx, '_get_runtime'):
            idx = idx._get_runtime()
        return BuiltIn._instances[idx]._obj

    def __rshift__(self, other):
        raise NotImplementedError('builtin object can not be assigned')

    def _generate_executable(self):
        raise NotImplementedError

    def _generate_init(self):
        raise NotImplementedError

    def _set_runtime(self, val):
        raise NotImplementedError

    def _check_callback(self):
        if self._callbacks is all_callbacks:
            return
        if self.in_init() and InitCallback in self._callbacks:
            return
        if KSP.callback() not in self._callbacks:
            raise RuntimeError(
                f'can be used only in {self._callbacks} callbacks'
            )

    @staticmethod
    def refresh():
        BuiltIn._id_count = int()
        BuiltIn._instances = list()


class BuilInVar(BuiltIn):
    def set_value(self, val):
        self._value = val


class BuiltInIntVar(BuilInVar, kInt):
    ''''''

    def __init__(
        self,
        name: str,
        callbacks=all_callbacks,
        def_val: int = 1
    ):
        BuiltIn.__init__(self, callbacks=callbacks)
        kInt.__init__(
            self,
            value=def_val,
            name=name,
            preserve=False,
            is_local=True,
            persist=False
        )


class BuiltInRealVar(BuilInVar, kReal):
    ''''''

    def __init__(
        self,
        name: str,
        callbacks=all_callbacks,
        def_val: float = 1.0
    ):
        BuiltIn.__init__(self, callbacks=callbacks)
        kReal.__init__(
            self,
            value=def_val,
            name=name,
            preserve=False,
            is_local=True,
            persist=False
        )


class BuiltInArray(BuiltIn, KspArray):
    def __init__(self, callbacks=all_callbacks):
        BuiltIn.__init__(self, callbacks=callbacks)

    def __setitem__(self, idx, val):
        raise NotImplementedError

    def set_value(self, idx, value):
        runtime_idx = idx
        if hasattr(idx, '_get_runtime'):
            runtime_idx = idx._get_runtime()
        self._item_set_runtime(self, runtime_idx, value)
        self._item_name(self, idx)

    def append(self, val):
        raise NotImplementedError

    def extend(self, val):
        raise NotImplementedError


class BuiltInArrayInt(BuiltInArray, kArrInt):
    def __init__(self, name, size, callbacks=all_callbacks):
        BuiltInArray.__init__(self, callbacks=callbacks)
        kArrInt.__init__(
            self,
            sequence=[0] * size,
            name=name,
            size=size,
            preserve=False,
            persist=False,
            is_local=True
        )


class BuiltInArrayReal(BuiltInArray, kArrReal):
    def __init__(self, name, size, callbacks=all_callbacks):
        BuiltInArray.__init__(self, callbacks=callbacks)
        kArrReal.__init__(
            self,
            sequence=[0.0] * size,
            name=name,
            size=size,
            preserve=False,
            persist=False,
            is_local=True
        )


class BuiltInFunc(BuiltIn):
    def __init__(
        self,
        name: str,
        callbacks=all_callbacks,
        args: OrderedDict = None,
        def_ret=None,
        no_parentesis=False
    ):
        self._name = name
        self._args = args
        self._def_ret = def_ret
        self._no_parentesis = no_parentesis
        super().__init__(callbacks=callbacks)
        partialmethod(self.__init__, self._args)
        functools.partial

    def _check_arg(self, key, val):
        native_val = val
        arg = self._args[key]
        if hasattr(val, 'get_value'):
            val = val.get_value()
        if arg is int:
            ref = (int, KspIntVar)
        elif arg is str:
            ref = (str, KspStrVar)
        elif arg is float:
            ref = (float, KspRealVar)
        else:
            ref = arg
        if not isinstance(val, ref):
            raise TypeError(
                f'arg "{key}" has to be of type {ref}. ' +
                f'pasted {type(val)}'
            )
        return native_val

    def __call__(self, *args):
        if not self._args:
            return self._build()
        passed = list()
        for arg, key in zip(args, self._args.keys()):
            passed.append(self._check_arg(key, arg))
        line = self._name + '('
        for idx, arg in enumerate(passed):
            if idx != 0:
                line += ', '
            if isinstance(arg, str):
                arg = f'"{arg}"'
            if hasattr(arg, '_get_compiled'):
                arg = arg._get_compiled()
            if hasattr(arg, 'expand'):
                arg = arg.expand()
            line += f'{arg}'
        line += ')'

        return self._build(line, passed)

    @staticmethod
    def _remove_line(self, line):
        if not self.is_compiled() or Output().blocked:
            return line
        try:
            line_l = Output().pop()
        except IndexError:
            return line
        if line_l == line:
            return line
        Output().put(line_l)
        return line

    def _build(self, line=None, args=None):
        if not self._def_ret:
            val = self.calculate(*args)
        else:
            val = self.calculate()
        self._var._set_runtime(val)
        if self._no_parentesis:
            line = self._name
        if not line:
            line = f'{self._name}()'
        self._var._get_compiled = lambda self=self:\
            BuiltInFunc._remove_line(self, line)
        self._var.name = self._var._get_compiled
        if self.is_compiled():
            Output().put(line)
        return self._var

    # @abstractmethod
    def calculate(self):
        return self._def_ret


class BuiltInFuncInt(BuiltInFunc):
    def __init__(
        self,
        name: str,
        callbacks=all_callbacks,
        args: OrderedDict = None,
        def_ret=None,
        no_parentesis=False
    ):
        BuiltInFunc.__init__(
            self,
            name=name,
            callbacks=callbacks,
            args=args,
            no_parentesis=no_parentesis,
            def_ret=def_ret
        )
        self._var = kInt(
            name=name,
            preserve=False,
            is_local=True,
            persist=False
        )


class BuiltInFuncStr(BuiltInFunc):
    def __init__(
        self,
        name: str,
        callbacks=all_callbacks,
        args: OrderedDict = None,
        def_ret=None,
        no_parentesis=False
    ):
        BuiltInFunc.__init__(
            self,
            name=name,
            callbacks=callbacks,
            args=args,
            no_parentesis=no_parentesis,
            def_ret=def_ret
        )
        self._var = kStr(
            name=name,
            preserve=False,
            is_local=True,
            persist=False
        )


class BuiltInFuncReal(BuiltInFunc):
    def __init__(
        self,
        name: str,
        callbacks=all_callbacks,
        args: OrderedDict = None,
        def_ret=None,
        no_parentesis=False
    ):
        BuiltInFunc.__init__(
            self,
            name=name,
            callbacks=callbacks,
            args=args,
            no_parentesis=no_parentesis,
            def_ret=def_ret
        )
        self._var = kReal(
            name=name,
            preserve=False,
            is_local=True,
            persist=False
        )


exit = BuiltInFuncInt(
    'exit',
    no_parentesis=True,
    def_ret=kNone()
).__call__
reset_ksp_timer = BuiltInFuncInt(
    'reset_ksp_timer',
    no_parentesis=True,
    def_ret=kNone()
).__call__
ignore_controller = BuiltInFuncInt(
    'ignore_controller',
    no_parentesis=True,
    def_ret=kNone()
).__call__


class MessageFunc(BuiltInFuncInt):
    def __init__(self, *args):
        super().__init__(
            'message',
            callbacks=all_callbacks,
            def_ret=kNone()
        )
        # self._old_call = BuiltInFuncInt.__call__

    def __call__(self, *args, sep: str = ', '):
        '''behaves like print in python. Just rints args not in stdout
        but in the bottom line of Kontakt GUI.
        For the logging purpose use kLog and logpr'''
        self._check_sep(sep)
        line = 'message('
        for idx, arg in enumerate(args):
            if idx != 0:
                line += f' & "{sep}" & '
            if isinstance(arg, str):
                arg = f'"{arg}"'
            if hasattr(arg, '_get_compiled'):
                arg = arg._get_compiled()
            if hasattr(arg, 'expand'):
                arg = arg.expand()
            line += f'{arg}'
        line += ')'
        return self._build(line=line, args=None)

    def _check_sep(self, sep):
        for char in sep:
            if char in ('\n', '\r', '\t', '\v'):
                raise AttributeError(
                    f'symbol {repr(char)} is not allowed'
                )


message = MessageFunc().__call__


class bCallbackVar(BuiltInIntVar):
    pass


NI_CALLBACK_ID = bCallbackVar('NI_CALLBACK_ID')
NI_CALLBACK_TYPE = bCallbackVar('NI_CALLBACK_TYPE')
NI_CB_TYPE_ASYNC_OUT = bCallbackVar('NI_CB_TYPE_ASYNC_OUT')
NI_CB_TYPE_CONTROLLER = bCallbackVar('NI_CB_TYPE_CONTROLLER')
NI_CB_TYPE_INIT = bCallbackVar('NI_CB_TYPE_INIT')
NI_CB_TYPE_LISTENER = bCallbackVar('NI_CB_TYPE_LISTENER')
NI_CB_TYPE_NOTE = bCallbackVar('NI_CB_TYPE_NOTE')
NI_CB_TYPE_PERSISTENCE_CHANGED = \
    bCallbackVar('NI_CB_TYPE_PERSISTENCE_CHANGED')
NI_CB_TYPE_PGS = bCallbackVar('NI_CB_TYPE_PGS')
NI_CB_TYPE_POLY_AT = bCallbackVar('NI_CB_TYPE_POLY_AT')
NI_CB_TYPE_RELEASE = bCallbackVar('NI_CB_TYPE_RELEASE')
NI_CB_TYPE_RPN = bCallbackVar('NI_CB_TYPE_RPN')
NI_CB_TYPE_NRPN = bCallbackVar('NI_CB_TYPE_NRPN')
NI_CB_TYPE_UI_CONTROL = bCallbackVar('NI_CB_TYPE_UI_CONTROL')
NI_CB_TYPE_UI_UPDATE = bCallbackVar('NI_CB_TYPE_UI_UPDATE')
NI_CB_TYPE_MIDI_IN = bCallbackVar('NI_CB_TYPE_MIDI_IN')

AsyncCompleteCallback = Callback(
    'async_complete',
    NI_CB_TYPE_ASYNC_OUT,
    ('NI_ASYNC_EXIT_STATUS',
     'NI_ASYNC_ID')
)
ControllerCallback = Callback(
    'controller',
    NI_CB_TYPE_CONTROLLER,
    ('CC_NUM',
     )
)
InitCallback = Callback('init', NI_CB_TYPE_INIT, tuple())
ListenerCallback = Callback(
    'listener',
    NI_CB_TYPE_LISTENER,
    ('NI_SIGNAL_TYPE',
     )
)
NoteCallback = Callback(
    'note',
    NI_CB_TYPE_NOTE,
    ('EVENT_NOTE',
     'EVENT_VELOCITY',
     'EVENT_ID')
)
PersistenceCallback = Callback(
    'persistence_changed',
    NI_CB_TYPE_PERSISTENCE_CHANGED,
    tuple()
)
PgsCallback = Callback('pgs_changed', NI_CB_TYPE_PGS, tuple())
PolyAtCallback = Callback(
    'poly_at',
    NI_CB_TYPE_POLY_AT,
    ('POLY_AT_NUM',
     )
)
ReleaseCallback = Callback(
    'release',
    NI_CB_TYPE_RELEASE,
    ('EVENT_NOTE',
     'EVENT_VELOCITY',
     'EVENT_ID')
)
MidiCallback = Callback(
    'midi_in',
    NI_CB_TYPE_MIDI_IN,
    ('MIDI_COMMAND',
     'MIDI_CHANNEL',
     'MIDI_BYTE_1',
     'MIDI_BYTE_2')
)
RpnCallback = Callback(
    'rpn',
    NI_CB_TYPE_RPN,
    ('RPN_ADDRESS',
     'RPN_VALUE')
)
NrpnCallback = Callback(
    'nrpn',
    NI_CB_TYPE_NRPN,
    ('RPN_ADDRESS',
     'RPN_VALUE')
)
UiUpdateCallback = Callback('ui_update', NI_CB_TYPE_UI_UPDATE, tuple())
UiControlCallback = UiControlCallbackCl(NI_CB_TYPE_UI_CONTROL)
FunctionCallback = FunctionCallbackCl()

CURRENT_SCRIPT_SLOT = BuiltInIntVar('CURRENT_SCRIPT_SLOT')
GROUPS_SELECTED = BuiltInArrayInt('GROUPS_SELECTED', 700)
NI_ASYNC_EXIT_STATUS = BuiltInIntVar(
    'NI_ASYNC_EXIT_STATUS',
    callbacks=(AsyncCompleteCallback,
               )
)
NI_ASYNC_ID = BuiltInIntVar(
    'NI_ASYNC_ID',
    callbacks=(AsyncCompleteCallback,
               )
)
NI_BUS_OFFSET = BuiltInIntVar('NI_BUS_OFFSET')
NUM_GROUPS = BuiltInIntVar('NUM_GROUPS')
NUM_OUTPUT_CHANNELS = BuiltInIntVar('NUM_OUTPUT_CHANNELS')
NUM_ZONES = BuiltInIntVar('NUM_ZONES')
PLAYED_VOICES_INST = BuiltInIntVar('PLAYED_VOICES_INST')
PLAYED_VOICES_TOTAL = BuiltInIntVar('PLAYED_VOICES_TOTAL')


class bPathVar(BuiltInIntVar):
    pass


GET_FOLDER_LIBRARY_DIR = bPathVar('GET_FOLDER_LIBRARY_DIR')
GET_FOLDER_FACTORY_DIR = bPathVar('GET_FOLDER_FACTORY_DIR')
GET_FOLDER_PATCH_DIR = bPathVar('GET_FOLDER_PATCH_DIR')


class bTmProVar(BuiltInIntVar):
    pass


NI_VL_TMPRO_STANDARD = bTmProVar('NI_VL_TMPRO_STANDARD')
NI_VL_TMRPO_HQ = bTmProVar('NI_VL_TMRPO_HQ')
REF_GROUP_IDX = BuiltInIntVar('REF_GROUP_IDX')
ALL_GROUPS = BuiltInIntVar('ALL_GROUPS')
ALL_EVENTS = BuiltInIntVar('ALL_EVENTS')

KEY_DOWN = BuiltInArrayInt('KEY_DOWN', 128)
KEY_DOWN_OCT = BuiltInArrayInt('KEY_DOWN_OCT', 12)
DISTANCE_BAR_START = BuiltInIntVar(
    'DISTANCE_BAR_START',
    callbacks=(NoteCallback,
               )
)
DURATION_BAR = BuiltInIntVar('DURATION_BAR')
DURATION_QUARTER = BuiltInIntVar('DURATION_QUARTER')
DURATION_EIGHTH = BuiltInIntVar('DURATION_EIGHTH')
DURATION_SIXTEENTH = BuiltInIntVar('DURATION_SIXTEENTH')
DURATION_QUARTER_TRIPLET = BuiltInIntVar('DURATION_QUARTER_TRIPLET')
DURATION_EIGHTH_TRIPLET = BuiltInIntVar('DURATION_EIGHTH_TRIPLET')
DURATION_SIXTEENTH_TRIPLET = BuiltInIntVar('DURATION_SIXTEENTH_TRIPLET')
ENGINE_UPTIME = BuiltInIntVar('ENGINE_UPTIME')
KSP_TIMER = BuiltInIntVar('KSP_TIMER')
NI_SONG_POSITION = BuiltInIntVar('NI_SONG_POSITION')
NI_TRANSPORT_RUNNING = BuiltInIntVar('NI_TRANSPORT_RUNNING')
SIGNATURE_NUM = BuiltInIntVar('SIGNATURE_NUM')
SIGNATURE_DENOM = BuiltInIntVar('SIGNATURE_DENOM')


class bTempoUnitVar(BuiltInIntVar):
    pass


NI_SYNC_UNIT_ABS = bTempoUnitVar('NI_SYNC_UNIT_ABS')
NI_SYNC_UNIT_WHOLE = bTempoUnitVar('NI_SYNC_UNIT_WHOLE')
NI_SYNC_UNIT_WHOLE_TRIPLET = bTempoUnitVar('NI_SYNC_UNIT_WHOLE_TRIPLET')
NI_SYNC_UNIT_HALF = bTempoUnitVar('NI_SYNC_UNIT_HALF')
NI_SYNC_UNIT_HALF_TRIPLET = bTempoUnitVar('NI_SYNC_UNIT_HALF_TRIPLET')
NI_SYNC_UNIT_QUARTER = bTempoUnitVar('NI_SYNC_UNIT_QUARTER')
NI_SYNC_UNIT_QUARTER_TRIPLET = bTempoUnitVar(
    'NI_SYNC_UNIT_QUARTER_TRIPLET'
)
NI_SYNC_UNIT_8TH = bTempoUnitVar('NI_SYNC_UNIT_8TH')
NI_SYNC_UNIT_8TH_TRIPLET = bTempoUnitVar('NI_SYNC_UNIT_8TH_TRIPLET')
NI_SYNC_UNIT_16TH = bTempoUnitVar('NI_SYNC_UNIT_16TH')
NI_SYNC_UNIT_16TH_TRIPLET = bTempoUnitVar('NI_SYNC_UNIT_16TH_TRIPLET')
NI_SYNC_UNIT_32ND = bTempoUnitVar('NI_SYNC_UNIT_32ND')
NI_SYNC_UNIT_32ND_TRIPLET = bTempoUnitVar('NI_SYNC_UNIT_32ND_TRIPLET')
NI_SYNC_UNIT_64TH = bTempoUnitVar('NI_SYNC_UNIT_64TH')
NI_SYNC_UNIT_64TH_TRIPLET = bTempoUnitVar('NI_SYNC_UNIT_64TH_TRIPLET')
NI_SYNC_UNIT_256TH = bTempoUnitVar('NI_SYNC_UNIT_256TH')
NI_SYNC_UNIT_ZONE = bTempoUnitVar('NI_SYNC_UNIT_ZONE')
NOTE_DURATION = BuiltInArrayInt('NOTE_DURATION', 128)


class bListenerConst(BuiltInIntVar):
    pass


NI_SIGNAL_TRANSP_STOP = bListenerConst('NI_SIGNAL_TRANSP_STOP')
NI_SIGNAL_TRANSP_START = bListenerConst('NI_SIGNAL_TRANSP_START')
NI_SIGNAL_TIMER_MS = bListenerConst('NI_SIGNAL_TIMER_MS')
NI_SIGNAL_TIMER_BEAT = bListenerConst('NI_SIGNAL_TIMER_BEAT')
NI_SIGNAL_TYPE = bListenerConst(
    'NI_SIGNAL_TYPE',
    callbacks=(ListenerCallback,
               )
)

NI_MATH_PI = BuiltInRealVar('NI_MATH_PI')
NI_MATH_E = BuiltInRealVar('NI_MATH_E')
NI_MATH_PI.set_value(math.pi)
NI_MATH_E.set_value(math.e)


class Exp(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='exp',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.exp(get_runtime_val(value))

    def __call__(self, value: float):
        '''exponential function (returns the value of e^x)'''
        return super().__call__(value)


exp = Exp().__call__


class IntToReal(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='int_to_real',
            args=OrderedDict(value=(KspIntVar,
                                    int,
                                    AstBase))
        )

    def calculate(self, value):
        return float(get_runtime_val(value))

    def __call__(self, value: int):
        '''exponential function (returns the value of e^x)'''
        return super().__call__(value)


int_to_real = IntToReal().__call__


class RealToInt(BuiltInFuncInt):
    def __init__(self):
        super().__init__(
            name='real_to_int',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        value = get_runtime_val(value)
        return int(value)

    def __call__(self, value: float):
        '''exponential function (returns the value of e^x)'''
        return super().__call__(value)


real_to_int = RealToInt().__call__


class AbsReal(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='abs',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return abs(get_runtime_val(value))


class AbsInt(BuiltInFuncInt):
    def __init__(self):
        super().__init__(
            name='abs',
            args=OrderedDict(value=(KspIntVar,
                                    int,
                                    AstBase))
        )

    def calculate(self, value):
        return abs(get_runtime_val(value))


abs_int = AbsInt()
abs_real = AbsReal()


def kabs(value: Union[KspIntVar, KspRealVar, AstBase, int, float]):
    '''Kontakt abs() Return absolute value.'''
    # print(get_runtime_val(value), value)
    if isinstance(get_runtime_val(value), float):
        return abs_real(value)
    return abs_int(value)


class Log(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='log',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        try:
            return math.log(get_runtime_val(value))
        except ValueError as e:
            print(get_runtime_val(value))
            raise e

    def __call__(self, value: float):
        '''logarithmic function'''
        return super().__call__(value)
        # return 0.0


log = Log().__call__


class Pow(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='pow',
            args=OrderedDict(
                x=(KspRealVar,
                   float,
                   AstBase),
                y=(KspRealVar,
                   float,
                   AstBase)
            )
        )

    def calculate(self, x, y):
        x = get_runtime_val(x)
        y = get_runtime_val(y)
        return x**y

    def __call__(self, x: float, y: float):
        '''power (returns the value of x^y)'''
        return super().__call__(x, y)


kpow = Pow().__call__


class Sqrt(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='sqrt',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.sqrt(get_runtime_val(value))

    def __call__(self, value: float):
        '''square root'''
        return super().__call__(value)


sqrt = Sqrt().__call__


class Ceil(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='ceil',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.ceil(get_runtime_val(value))

    def __call__(self, value: float):
        '''ceiling (round up)
        ceil(2.3) = 3.0'''
        return super().__call__(value)


ceil = Ceil().__call__


class Floor(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='floor',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.floor(get_runtime_val(value))

    def __call__(self, value: float):
        '''floor (round down)
        floor(2.8) = 2.0'''
        return super().__call__(value)


floor = Floor().__call__


class Round(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='round',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return round(get_runtime_val(value))

    def __call__(self, value: float):
        '''round (round to nearest)
        round(2.3) = 2.0
        round(2.8) = 3.0'''
        return super().__call__(value)


kround = Round().__call__


class Cos(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='cos',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.cos(get_runtime_val(value))

    def __call__(self, value: float):
        '''cosine function'''
        return super().__call__(value)


cos = Cos().__call__


class Sin(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='sin',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.sin(get_runtime_val(value))

    def __call__(self, value: float):
        '''sine function'''
        return super().__call__(value)


sin = Sin().__call__


class Tan(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='tan',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.tan(get_runtime_val(value))

    def __call__(self, value: float):
        '''tangent function'''
        return super().__call__(value)


tan = Tan().__call__


class Acos(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='acos',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.acos(get_runtime_val(value))

    def __call__(self, value: float):
        '''arccosine (inverse cosine function)'''
        return super().__call__(value)


acos = Acos().__call__


class Asin(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='asin',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.asin(get_runtime_val(value))

    def __call__(self, value: float):
        '''arccosine (inverse cosine function)'''
        return super().__call__(value)


asin = Asin().__call__


class Atan(BuiltInFuncReal):
    def __init__(self):
        super().__init__(
            name='atan',
            args=OrderedDict(value=(KspRealVar,
                                    float,
                                    AstBase))
        )

    def calculate(self, value):
        return math.atan(get_runtime_val(value))

    def __call__(self, value: float):
        '''arccosine (inverse cosine function)'''
        return super().__call__(value)


atan = Atan().__call__


class Random(BuiltInFuncInt):
    def __init__(self):
        super().__init__(
            name='random',
            args=OrderedDict(
                _min=(KspIntVar,
                      int,
                      AstBase),
                _max=(KspIntVar,
                      int,
                      AstBase)
            )
        )

    def calculate(self, _min, _max):
        return random.randint(
            get_runtime_val(_min),
            get_runtime_val(_max)
        )

    def __call__(self, _min: int, _max: int):
        '''return random int between min and max'''
        return super().__call__(_min, _max)


krandom = Random().__call__
