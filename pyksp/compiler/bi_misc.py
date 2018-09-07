from collections import OrderedDict

from abstract import KSP
from abstract import SingletonMeta
from abstract import Output

from base_types import KspStrVar
from base_types import KspIntVar

from k_built_ins import InitCallback
from k_built_ins import BuiltInFuncInt
from k_built_ins import BuiltInFuncStr
from k_built_ins import get_runtime_val
from k_built_ins import bListenerConst
from k_built_ins import BuiltInIntVar

from bi_load_save import save_array
from bi_load_save import save_array_str


from base_types import KspArray

from functions import func
from base_types import AstEq

from native_types import kArrStr
from native_types import kInt

from native_types import kNone
from native_types import kArrInt

from conditions_loops import While
from conditions_loops import If
# from conditions_loops import Else
from conditions_loops import check


class ArrayEqual(BuiltInFuncInt):

    def __init__(self):
        super().__init__('array_equal',
                         args=OrderedDict(array_1=KspArray,
                                          array_2=KspArray))

    def __call__(self, array_1: KspArray, array_2: KspArray):
        '''checks the values of two arrays, true if all values are equal,
        false if not'''
        return super().__call__(array_1, array_2)

    def calculate(self, array_1, array_2):
        for f, s in zip(array_1.iter_runtime(), array_2.iter_runtime()):
            if f._get_runtime() != s._get_runtime():
                return 0
        return 1


array_equal = ArrayEqual().__call__


class NumElements(BuiltInFuncInt):

    def __init__(self):
        super().__init__('num_elements',
                         args=OrderedDict(array=KspArray))

    def __call__(self, array: KspArray):
        '''returns the number of elements in an array'''
        return super().__call__(array)

    def calculate(self, array):
        return len(array)


num_elements = NumElements().__call__


class Search(BuiltInFuncInt):

    def __init__(self):
        super().__init__('search',
                         args=OrderedDict(array=kArrInt, value=int))

    def __call__(self, array: kArrInt, value: int):
        '''returns the number of elements in an array'''
        return super().__call__(array, value)

    def calculate(self, array, value):
        if hasattr(value, '_get_runtime'):
            value = value._get_runtime()
        if hasattr(value, 'get_value'):
            value = value.get_value()
        for idx, item in enumerate(array.iter_runtime()):
            if item._get_runtime() == value:
                return idx


search = Search().__call__


class Sort(BuiltInFuncInt):

    def __init__(self):
        super().__init__('sort',
                         args=OrderedDict(array=kArrInt, direction=int))

    def __call__(self, array: kArrInt, direction: int):
        '''returns the number of elements in an array'''
        return super().__call__(array, direction)

    def calculate(self, array, direction):
        if hasattr(direction, '_get_runtime'):
            direction = direction._get_runtime()
        if hasattr(direction, 'get_value'):
            direction = direction.get_value()
        array._sort(direction)
        return kNone()


sort = Sort().__call__


class AllowGroup(BuiltInFuncInt):

    def __init__(self):
        super().__init__('allow_group',
                         args=OrderedDict(group_idx=int),
                         def_ret=kNone())

    def __call__(self, group_idx: int):
        '''allows the specified group, i.e.
        makes it available for playback
        Remarks
        • The numbering of the group index is zero based, i.e. the first
        group has the group index 0.
        • The groups can only be changed if the voice is not running.'''
        return super().__call__(group_idx)


allow_group = AllowGroup().__call__


class DisAllowGroup(BuiltInFuncInt):

    def __init__(self):
        super().__init__('disallow_group',
                         args=OrderedDict(group_idx=int),
                         def_ret=kNone())

    def __call__(self, group_idx: int):
        '''disallows the specified group, i.e. makes it unavailable for
        playback
        Remarks
        • The numbering of the group index is zero based, i.e. the first
        group has the group index 0.
        • The groups can only be changed if the voice is not running.'''
        return super().__call__(group_idx)


disallow_group = DisAllowGroup().__call__


class FindGroup(BuiltInFuncInt):

    def __init__(self):
        super().__init__('find_group',
                         args=OrderedDict(group_name=str),
                         def_ret=1)

    def __call__(self, group_name: str):
        '''returns the group index for the specified group name
        Remarks
        If no group with the specified name is found, this command will
        return the value zero. This can cause problems as this is the
        group index of the first group, so be careful when using this
        command.'''
        return super().__call__(group_name)


find_group = FindGroup().__call__


class GetPurgeState(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_purge_state',
                         args=OrderedDict(group_idx=int),
                         def_ret=1)

    def __call__(self, group_idx: int):
        '''returns the purge state of the specified group:
        0: the group is purged (0)
        1: the group is not purged, i.e. the samples are loaded
        <group-index>
        the index number of the group that should be checked'''
        return super().__call__(group_idx)


get_purge_state = GetPurgeState().__call__


class GroupName(BuiltInFuncStr):

    def __init__(self):
        super().__init__('group_name',
                         args=OrderedDict(group_idx=int),
                         def_ret='group_name')

    def __call__(self, group_idx: int):
        '''returns the group name for the specified group
        Remarks
        The numbering of the group index is zero based, i.e. the first
        group has the group index 0.'''
        return super().__call__(group_idx)


group_name = GroupName().__call__


class PurgeGroup(BuiltInFuncInt):

    def __init__(self):
        super().__init__('purge_group',
                         args=OrderedDict(group_idx=int, value=int),
                         def_ret=kNone())

    def __call__(self, group_idx: int, value: int):
        '''purges (i.e. unloads from RAM) the samples of the specified
        group
        <group-index>
        the index number of the group which contains the samples to be
        purged
        <mode>
        If set to 0, the samples of the specified group are unloaded.
        If set to 1, the samples are reloaded.'''
        return super().__call__(group_idx, value)


purge_group = PurgeGroup().__call__


class ChangeListener(BuiltInFuncInt):

    def __init__(self):
        super().__init__('change_listener_par',
                         args=OrderedDict(signal_type=bListenerConst,
                                          value=int),
                         def_ret=kNone())

    def __call__(self, signal_type: bListenerConst, value: int):
        '''changes the parameters of the on listener callback.
        Can be used in every callback.
        <signal-type>
        The signal to be changed, can be either:
        $NI_SIGNAL_TIMER_MS
        $NI_SIGNAL_TIMER_BEAT
        <parameter>
        dependent on the specified signal type:
        $NI_SIGNAL_TIMER_MS
        time interval in microseconds
        $NI_SIGNAL_TIMER_BEAT
        time interval in fractions of a beat/quarter note'''
        return super().__call__(signal_type, value)


change_listener_par = ChangeListener().__call__


class MsToTicks(BuiltInFuncInt):

    def __init__(self):
        super().__init__('ms_to_ticks',
                         args=OrderedDict(microseconds=int),
                         def_ret=1)

    def __call__(self, microseconds: int):
        '''converts a microseconds value into a tempo
        dependent ticks value'''
        return super().__call__(microseconds)


ms_to_ticks = MsToTicks().__call__


class TicksToMs(BuiltInFuncInt):

    def __init__(self):
        super().__init__('ticks_to_ms',
                         args=OrderedDict(ticks=int),
                         def_ret=1)

    def __call__(self, ticks: int):
        '''converts a tempo dependent ticks value into a
        microseconds value'''
        return super().__call__(ticks)


ticks_to_ms = TicksToMs().__call__


class SetListener(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_listener',
                         args=OrderedDict(signal_type=bListenerConst,
                                          value=int),
                         def_ret=kNone(),
                         callbacks=(InitCallback,))

    def __call__(self, signal_type: bListenerConst, value: int):
        '''Sets the signals on which the listener callback should
        react to. Can only be used in the init callback.
        <signal-type>
        the event on which the listener callback should react.
        The following types are available:
        $NI_SIGNAL_TRANSP_STOP
        $NI_SIGNAL_TRANSP_START
        $NI_SIGNAL_TIMER_MS
        $NI_SIGNAL_TIMER_BEAT
        <parameter>
        user defined parameter, dependant on the specified signal type:
        $NI_SIGNAL_TIMER_MS
        time interval in microseconds
        $NI_SIGNAL_TIMER_BEAT
        time interval in fractions of a beat/quarter note
        $NI_SIGNAL_TRANSP_START
        set to 1 if the listener callback should react to the host's
        transport start command
        $NI_SIGNAL_TRANSP_STOP
        set to 1 if the listener callback should react to the host's
        transport stop command
        Remarks
        When using $NI_SIGNAL_TIMER_BEAT, the maxium resolution is
        24 ticks per beat/quarter note.'''
        return super().__call__(signal_type, value)


set_listener = SetListener().__call__


class StopWait(BuiltInFuncInt):

    def __init__(self):
        super().__init__('stop_wait',
                         args=OrderedDict(callback_id=int,
                                          parameter=int),
                         def_ret=kNone())

    def __call__(self, callback_id: int, parameter: int):
        '''stops wait commands in the specified callback
        <callback-ID>
        the callback’s ID number in which the wait commands will be
        stopped
        <parameter>
        0: stops only the current wait
        1: stops the current wait and ignores all following wait commands
        in this callback.'''
        return super().__call__(callback_id, parameter)


stop_wait = StopWait().__call__


class Wait(BuiltInFuncInt):

    def __init__(self):
        super().__init__('wait',
                         args=OrderedDict(microseconds=int),
                         def_ret=kNone())

    def __call__(self, microseconds: int):
        '''pauses the callback for the specified time in microseconds'''
        return super().__call__(microseconds)


wait = Wait().__call__


class WaitTicks(BuiltInFuncInt):

    def __init__(self):
        super().__init__('wait_ticks',
                         args=OrderedDict(ticks=int),
                         def_ret=kNone())

    def __call__(self, ticks: int):
        '''pauses the callback for the specified time in ticks'''
        return super().__call__(ticks)


wait_ticks = WaitTicks().__call__

# KEYS


class bKeyType(BuiltInIntVar):
    pass


NI_KEY_TYPE_DEFAULT = bKeyType('NI_KEY_TYPE_DEFAULT')
NI_KEY_TYPE_CONTROL = bKeyType('NI_KEY_TYPE_CONTROL')
NI_KEY_TYPE_NONE = bKeyType('NI_KEY_TYPE_NONE')


class key_color(BuiltInIntVar):

    def _get_item(note_nr):
        if hasattr(note_nr, '_get_runtime'):
            note_nr = note_nr._get_runtime()
        if hasattr(note_nr, 'get_value'):
            note_nr = note_nr.get_value()
        if not KSP.is_compiled():
            color = keys[note_nr].color
        return color
        return keys[note_nr].color

    def _set_item(note_nr, color):
        if not KSP.is_compiled():
            color = color.id
        keys[note_nr].color = color


KEY_COLOR_RED = key_color('KEY_COLOR_RED')
KEY_COLOR_ORANGE = key_color('KEY_COLOR_ORANGE')
KEY_COLOR_LIGHT_ORANGE = key_color('KEY_COLOR_LIGHT_ORANGE')
KEY_COLOR_WARM_YELLOW = key_color('KEY_COLOR_WARM_YELLOW')
KEY_COLOR_YELLOW = key_color('KEY_COLOR_YELLOW')
KEY_COLOR_LIME = key_color('KEY_COLOR_LIME')
KEY_COLOR_GREEN = key_color('KEY_COLOR_GREEN')
KEY_COLOR_MINT = key_color('KEY_COLOR_MINT')
KEY_COLOR_CYAN = key_color('KEY_COLOR_CYAN')
KEY_COLOR_TURQUOISE = key_color('KEY_COLOR_TURQUOISE')
KEY_COLOR_BLUE = key_color('KEY_COLOR_BLUE')
KEY_COLOR_PLUM = key_color('KEY_COLOR_PLUM')
KEY_COLOR_VIOLET = key_color('KEY_COLOR_VIOLET')
KEY_COLOR_PURPLE = key_color('KEY_COLOR_PURPLE')
KEY_COLOR_MAGENTA = key_color('KEY_COLOR_MAGENTA')
KEY_COLOR_FUCHSIA = key_color('KEY_COLOR_FUCHSIA')
KEY_COLOR_DEFAULT = key_color('KEY_COLOR_DEFAULT')
KEY_COLOR_INACTIVE = key_color('KEY_COLOR_INACTIVE')
KEY_COLOR_NONE = key_color('KEY_COLOR_NONE')


class Key(KSP):
    pressed_support = False

    def __init__(self, nr):
        self.color = KEY_COLOR_NONE.id
        self.name = ''
        self._pressed = False
        self._type = NI_KEY_TYPE_NONE

    @property
    def pressed(self):

        return self._pressed

    @pressed.setter
    def pressed(self, val):
        if not self.pressed_support:
            raise RuntimeError(
                'pressed is not supported.' +
                f'use built_in {set_key_pressed_support}(1) before')
        self._pressed = bool(val)

    @property
    def type(self):
        return self._type.id

    @type.setter
    def type(self, val):
        self._type = val


keys = [Key(idx) for idx in range(128)]


class GetKeyColor(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_key_color',
                         args=OrderedDict(note_nr=int))

    def __call__(self, note_nr: int):
        '''returns the color constant of the specified note number
        can be compared to the key_color class variables'''
        return super().__call__(note_nr)

    def calculate(self, note_nr):
        return key_color._get_item(note_nr)


get_key_color = GetKeyColor().__call__


class SetKeyColor(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_key_color',
                         args=OrderedDict(note_nr=int,
                                          color=key_color),
                         def_ret=kNone())

    def __call__(self, note_nr: int, color: key_color):
        '''sets the color of the specified key (i.e. MIDI note) on
        the KONTAKT keyboard.
        The following colors are available:
        $KEY_COLOR_RED
        $KEY_COLOR_ORANGE
        $KEY_COLOR_LIGHT_ORANGE
        $KEY_COLOR_WARM_YELLOW
        $KEY_COLOR_YELLOW
        $KEY_COLOR_LIME
        $KEY_COLOR_GREEN
        $KEY_COLOR_MINT
        $KEY_COLOR_CYAN
        $KEY_COLOR_TURQUOISE
        $KEY_COLOR_BLUE
        $KEY_COLOR_PLUM
        $KEY_COLOR_VIOLET
        $KEY_COLOR_PURPLE
        $KEY_COLOR_MAGENTA
        $KEY_COLOR_FUCHSIA
        $KEY_COLOR_DEFAULT (sets the key to KONTAKT's standard color for
        mapped notes)
        $KEY_COLOR_INACTIVE (resets the key to standard black and white)
        $KEY_COLOR_NONE (resets the key to its normal KONTAKT color, e.g.
        red for internal keyswitches)'''
        key_color._set_item(note_nr, color)
        return super().__call__(note_nr, color)


set_key_color = SetKeyColor().__call__


class GetKeyName(BuiltInFuncStr):

    def __init__(self):
        super().__init__('get_key_name',
                         args=OrderedDict(note_nr=int))

    def __call__(self, note_nr: int):
        '''returns the name of the specified key'''
        return super().__call__(note_nr)

    def calculate(self, note_nr):
        note_nr = get_runtime_val(note_nr)
        return keys[note_nr].name


get_key_name = GetKeyName().__call__


class SetKeyName(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_key_name',
                         args=OrderedDict(note_nr=int, name=str))

    def __call__(self, note_nr: int, name: str):
        '''assigns a text string to the specified key'''
        return super().__call__(note_nr, name)

    def calculate(self, note_nr, name):
        note_nr = get_runtime_val(note_nr)
        name = get_runtime_val(name)
        keys[note_nr].name = name
        return kNone()


set_key_name = SetKeyName().__call__


class GetKeyTriggerstate(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_key_triggerstate',
                         args=OrderedDict(note_nr=int))

    def __call__(self, note_nr: int):
        '''returns the name of the specified key'''
        return super().__call__(note_nr)

    def calculate(self, note_nr):
        note_nr = get_runtime_val(note_nr)
        return keys[note_nr].pressed


get_key_triggerstate = GetKeyTriggerstate().__call__


class GetKeyType(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_key_type',
                         args=OrderedDict(note_nr=int))

    def __call__(self, note_nr: int):
        '''returns the name of the specified key'''
        return super().__call__(note_nr)

    def calculate(self, note_nr):
        note_nr = get_runtime_val(note_nr)
        return keys[note_nr].type


get_key_type = GetKeyType().__call__


class GetKeyRangeMinNote(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_keyrange_min_note',
                         args=OrderedDict(note_nr=int),
                         def_ret=1)

    def __call__(self, note_nr: int):
        '''returns the lowest note of the specified key range'''
        return super().__call__(note_nr)


get_keyrange_min_note = GetKeyRangeMinNote().__call__


class GetKeyRangeMaxNote(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_keyrange_max_note',
                         args=OrderedDict(note_nr=int),
                         def_ret=1)

    def __call__(self, note_nr: int):
        '''returns the highest note of the specified key range'''
        return super().__call__(note_nr)


get_keyrange_max_note = GetKeyRangeMaxNote().__call__


class GetKeyRangeMaxNote(BuiltInFuncStr):

    def __init__(self):
        super().__init__('get_keyrange_name',
                         args=OrderedDict(note_nr=int),
                         def_ret='keyrange')

    def __call__(self, note_nr: int):
        '''returns the name of the specified key range'''
        return super().__call__(note_nr)


get_keyrange_name = GetKeyRangeMaxNote().__call__


class SetKeyPressed(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_key_pressed',
                         args=OrderedDict(note_nr=int, value=int))

    def __call__(self, note_nr: int, value: int):
        '''sets the trigger state of the specified key on KONTAKT's
        keyboard either to pressed/on (1) or released/off (0)'''
        return super().__call__(note_nr, value)

    def calculate(self, note_nr, value):
        note_nr = get_runtime_val(note_nr)
        value = get_runtime_val(value)
        keys[note_nr].pressed = bool(value)
        return kNone()


set_key_pressed = SetKeyPressed().__call__


class SetKeyPressedSupport(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_key_pressed_support',
                         args=OrderedDict(mode=int),
                         def_ret=kNone())

    def __call__(self, mode: int):
        '''sets the trigger state of the specified key on KONTAKT's
        keyboard either to pressed/on (1) or released/off (0)'''
        mode_r = get_runtime_val(mode)
        Key.pressed_support = mode_r
        return super().__call__(mode)


set_key_pressed_support = SetKeyPressedSupport().__call__


class SetKeyType(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_key_type',
                         args=OrderedDict(note_nr=int, value=bKeyType))

    def __call__(self, note_nr: int, value: bKeyType):
        '''assigns a key type to the specified key.
        The following key types are available:
        $NI_KEY_TYPE_DEFAULT (i.e. normal mapped notes that produce sound)
        $NI_KEY_TYPE_CONTROL (i.e. key switches or other notes that do
            not produce sound)
        $NI_KEY_TYPE_NONE (resets the key to its normal KONTAKT behaviour)
        '''
        return super().__call__(note_nr, value)

    def calculate(self, note_nr, value):
        note_nr = get_runtime_val(note_nr)
        keys[note_nr].type = value
        return kNone()


set_key_type = SetKeyType().__call__


class SetKeyrange(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_keyrange',
                         args=OrderedDict(min=int, max=int, name=str),
                         def_ret=kNone())

    def __call__(self, min: int, max: int, name: str):
        '''assigns a text string to the specified range of keys.
        Remarks
        Key ranges are instrument parameters and reside outside KSP, i.e.
        changing the key range is similar to changing a KONTAKT knob with
        set_engine_par(). Make sure to always remove all key ranges in the
        init callback or whenever changed later.
        There can be up to 16 key ranges per instrument.
        Key names and ranges are displayed in KONTAKT's info pane when
        hovering the mouse over the key on the KONTAKT keyboard. The range
        name is followed by the key name (separated by a dash).'''
        return super().__call__(min, max)


set_keyrange = SetKeyrange().__call__


class RemoveKeyrange(BuiltInFuncInt):

    def __init__(self):
        super().__init__('remove_keyrange',
                         args=OrderedDict(note_nr=int),
                         def_ret=kNone())

    def __call__(self, note_nr: int):
        '''assigns a text string to the specified range of keys
        Remarks
        Key ranges are instrument parameters and reside outside KSP,
        i.e. changing the key range is similar to changing a KONTAKT
        knob with set_engine_par(). Make sure to always remove all key
        ranges in the init callback or whenever changed later.'''
        return super().__call__(note_nr)


remove_keyrange = RemoveKeyrange().__call__


class ConditiionSymbol:

    def __init__(self, symbol: str):
        self._name = symbol

    def _get_compiled(self):
        return self._name


NO_SYS_SCRIPT_GROUP_START = ConditiionSymbol('NO_SYS_SCRIPT_GROUP_START')
NO_SYS_SCRIPT_PEDAL = ConditiionSymbol('NO_SYS_SCRIPT_PEDAL')
NO_SYS_SCRIPT_RLS_TRIG = ConditiionSymbol('NO_SYS_SCRIPT_RLS_TRIG')


class SetCondition(BuiltInFuncInt):

    def __init__(self):
        super().__init__('SET_CONDITION',
                         args=OrderedDict(condition=ConditiionSymbol),
                         def_ret=kNone())

    def __call__(self, condition: ConditiionSymbol):
        '''used to set system KONTAKT parameters
        USE_CODE_IF, USE_CODE_IF_NOT are deprecated, so
        only condition symbols can be set are:
        NO_SYS_SCRIPT_GROUP_START - turn off group_strat engine
        NO_SYS_SCRIPT_PEDAL - turn off cc64 interpretation as pedal
        NO_SYS_SCRIPT_RLS_TRIG - don't chegne bahaviour of groups, marked
        as release_trigger'''
        return super().__call__(condition)


SET_CONDITION = SetCondition().__call__


class ResetCondition(BuiltInFuncInt):

    def __init__(self):
        super().__init__('RESET_CONDITION',
                         args=OrderedDict(condition=ConditiionSymbol),
                         def_ret=kNone())

    def __call__(self, condition: ConditiionSymbol):
        '''used to reset system KONTAKT parameters
        USE_CODE_IF, USE_CODE_IF_NOT are deprecated, so
        only condition symbols can be set are:
        NO_SYS_SCRIPT_GROUP_START
        NO_SYS_SCRIPT_PEDAL
        NO_SYS_SCRIPT_RLS_TRIG'''
        return super().__call__(condition)


RESET_CONDITION = ResetCondition().__call__


class FindZone(BuiltInFuncInt):

    def __init__(self):
        super().__init__('find_zone',
                         args=OrderedDict(zone_name=str),
                         def_ret=1)

    def __call__(self, zone_name: str):
        '''returns the zone ID for the specified zone name.
        Only availabe in the init callback.'''
        return super().__call__(zone_name)


find_zone = FindZone().__call__


class GetSampleLength(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_sample_length',
                         args=OrderedDict(zone_id=int),
                         def_ret=1)

    def __call__(self, zone_id: int):
        '''returns the length of the specified zone's
        sample in microseconds'''
        return super().__call__(zone_id)


get_sample_length = GetSampleLength().__call__


class NumSlicesZone(BuiltInFuncInt):

    def __init__(self):
        super().__init__('num_slices_zone',
                         args=OrderedDict(zone_id=int),
                         def_ret=1)

    def __call__(self, zone_id: int):
        '''returns the number of slices of the specified zone'''
        return super().__call__(zone_id)


num_slices_zone = NumSlicesZone().__call__


class ZoneSliceLength(BuiltInFuncInt):

    def __init__(self):
        super().__init__('zone_slice_length',
                         args=OrderedDict(zone_id=int,
                                          slice_idx=int),
                         def_ret=1)

    def __call__(self, zone_id: int, slice_idx: int):
        '''returns the length in microseconds of the specified
        slice with respect to the current tempo'''
        return super().__call__(zone_id, slice_idx)


zone_slice_length = ZoneSliceLength().__call__


class ZoneSliceStart(BuiltInFuncInt):

    def __init__(self):
        super().__init__('zone_slice_start',
                         args=OrderedDict(zone_id=int,
                                          slice_idx=int),
                         def_ret=1)

    def __call__(self, zone_id: int, slice_idx: int):
        '''returns the absolute start point of the specified
        slice in microseconds, independent of the current tempo'''
        return super().__call__(zone_id, slice_idx)


zone_slice_start = ZoneSliceStart().__call__


class ZoneLoopStart(BuiltInFuncInt):

    def __init__(self):
        super().__init__('zone_slice_idx_loop_start',
                         args=OrderedDict(zone_id=int,
                                          loop_idx=int),
                         def_ret=1)

    def __call__(self, zone_id: int, loop_idx: int):
        '''returns the index number of the slice at the loop start'''
        return super().__call__(zone_id, loop_idx)


zone_slice_idx_loop_start = ZoneLoopStart().__call__


class ZoneLoopEnd(BuiltInFuncInt):

    def __init__(self):
        super().__init__('zone_slice_idx_loop_end',
                         args=OrderedDict(zone_id=int,
                                          loop_idx=int),
                         def_ret=1)

    def __call__(self, zone_id: int, loop_idx: int):
        '''returns the index number of the slice at the loop end'''
        return super().__call__(zone_id, loop_idx)


zone_slice_idx_loop_end = ZoneLoopEnd().__call__


class ZoneLoopCount(BuiltInFuncInt):

    def __init__(self):
        super().__init__('zone_slice_loop_count',
                         args=OrderedDict(zone_id=int,
                                          loop_idx=int),
                         def_ret=1)

    def __call__(self, zone_id: int, loop_idx: int):
        '''returns the loop count of the specified loop'''
        return super().__call__(zone_id, loop_idx)


zone_slice_loop_count = ZoneLoopCount().__call__


class DontUseMachineMode(BuiltInFuncInt):

    def __init__(self):
        super().__init__('dont_use_machine_mode',
                         args=OrderedDict(event_id=int),
                         def_ret=1)

    def __call__(self, event_id: int):
        '''play the specified event in sampler mode'''
        return super().__call__(event_id)


dont_use_machine_mode = DontUseMachineMode().__call__


class PgsKey:

    def __init__(self, size, is_str):
        self._is_str = is_str
        if is_str:
            item = ''
        else:
            item = 0
        self._vals = list([item] * size)

    def set(self, idx, val):
        if self._is_str:
            assert isinstance(val, (str, KspStrVar))
        else:
            assert isinstance(val, (int, KspIntVar))
        self._vals[idx] = val

    def get(self, idx):
        return self._vals[idx]


class PGS(metaclass=SingletonMeta):

    def __init__(self):
        self._keys_int = dict()
        self._keys_str = dict()

    def key_exists(self, key: str):
        return key in self._keys_int

    def str_key_exists(self, key: str):
        return key in self._keys_int

    def create_key(self, key: str, size):
        self._keys_int[key] = PgsKey(size, False)

    def create_str_key(self, key: str):
        self._keys_str[key] = PgsKey(1, True)

    def set_key_val(self, key: str, idx: int, val: int):
        self._keys_int[key].set(idx, val)

    def set_str_key_val(self, key: str, val: str):
        self._keys_str[key].set(0, val)

    def get_key_val(self, key: str, idx: int):
        return self._keys_int[key].get(idx)

    def get_str_key_val(self, key: str):
        return self._keys_str[key].get(0)


class PgsKeyConverter:

    def __init__(self, key):
        if not isinstance(key, str):
            raise TypeError(f'key has to be {str}')
        self._key = key

    def _get_compiled(self):
        return self._key

    def _get_runtime(self):
        return self._key

    @property
    def val(self):
        return self._key


class PgsCreateKey(BuiltInFuncInt):

    def __init__(self):
        super().__init__('pgs_create_key',
                         args=OrderedDict(key=PgsKeyConverter,
                                          size=int),
                         def_ret=kNone())

    def __call__(self, key: str,
                 size: int):
        '''create int PGS key to be used as cross_script comunication.
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        PGS().create_key(key.val, size)
        return super().__call__(key, size)


pgs_create_key = PgsCreateKey().__call__


class PgsCreateKeyStr(BuiltInFuncInt):

    def __init__(self):
        super().__init__('pgs_create_str_key',
                         args=OrderedDict(key=PgsKeyConverter),
                         def_ret=kNone())

    def __call__(self, key: str):
        '''create str PGS key to be used as cross_script comunication.
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        PGS().create_str_key(key.val)
        return super().__call__(key)


pgs_create_str_key = PgsCreateKeyStr().__call__


class PgsKeyExsists(BuiltInFuncInt):

    def __init__(self):
        super().__init__('pgs_key_exists',
                         args=OrderedDict(key=PgsKeyConverter))

    def __call__(self, key: str):
        '''returns 1 if int key exsists
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        return super().__call__(key)

    def calculate(self, key):
        if PGS().key_exists(key.val):
            return 1
        return 0


pgs_key_exists = PgsKeyExsists().__call__


class PgsStrKeyExsists(BuiltInFuncInt):

    def __init__(self):
        super().__init__('pgs_str_key_exists',
                         args=OrderedDict(key=PgsKeyConverter))

    def __call__(self, key: str):
        '''returns 1 if str key exsists
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        return super().__call__(key)

    def calculate(self, key):
        if PGS().str_key_exists(key.val):
            return 1
        return 0


pgs_str_key_exists = PgsStrKeyExsists().__call__


class PgsSetKeyVal(BuiltInFuncInt):

    def __init__(self):
        super().__init__('pgs_set_key_val',
                         args=OrderedDict(key=PgsKeyConverter,
                                          idx=int, val=int),
                         def_ret=kNone())

    def __call__(self, key: str,
                 idx: int, val: int):
        '''sets value of PGS integer key at idx
        raises IndexError if idx is invalid
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        idx = get_runtime_val(idx)
        val = get_runtime_val(val)
        PGS().set_key_val(key.val, idx, val)
        return super().__call__(key, idx, val)


pgs_set_key_val = PgsSetKeyVal().__call__


class PgsSetStrKeyVal(BuiltInFuncInt):

    def __init__(self):
        super().__init__('pgs_set_str_key_val',
                         args=OrderedDict(key=PgsKeyConverter, val=str),
                         def_ret=kNone())

    def __call__(self, key: str, val: str):
        '''sets value of PGS string key at idx
        raises IndexError if idx is invalid
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        val = get_runtime_val(val)
        PGS().set_str_key_val(key.val, val)
        return super().__call__(key, val)


pgs_set_str_key_val = PgsSetStrKeyVal().__call__


class PgsGetKeyVal(BuiltInFuncInt):

    def __init__(self):
        super().__init__('pgs_get_key_val',
                         args=OrderedDict(key=PgsKeyConverter,
                                          idx=int))

    def __call__(self, key: str, idx: int):
        '''returns value of PGS integer key at idx
        raises IndexError if idx is invalid
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        return super().__call__(key, idx)

    def calculate(self, key, idx):
        key = get_runtime_val(key)
        idx = get_runtime_val(idx)
        return PGS().get_key_val(key, idx)


pgs_get_key_val = PgsGetKeyVal().__call__


class PgsGetStrKeyVal(BuiltInFuncStr):

    def __init__(self):
        super().__init__('pgs_get_str_key_val',
                         args=OrderedDict(key=PgsKeyConverter))

    def __call__(self, key: str):
        '''returns value of PGS string key at idx
        raises IndexError if idx is invalid
        instead of original KSP, key has to be string'''
        key = PgsKeyConverter(key)
        return super().__call__(key)

    def calculate(self, key):
        key = get_runtime_val(key)
        return PGS().get_str_key_val(key)


pgs_get_str_key_val = PgsGetStrKeyVal().__call__


def logpr(*args, sep=' '):
    try:
        kLog().put(*args, sep=sep)
    except TypeError as e:
        if str(e).startswith('__init__()'):
            pass
        else:
            raise e


class kLog(metaclass=SingletonMeta):

    array = object()
    label = object()
    pgs = object()

    pgs_script = \
        '''on init
      set_script_title("log_viever")
      declare ui_label $log_label(6, 4) 
      set_control_par_str(get_ui_id($log_label),$CONTROL_PAR_TEXT,...\
      "log started")
    end on

    on pgs_changed
      if (pgs_get_key_val(_log_flag,0)=1)
        pgs_set_key_val(_log_flag,0,0)
        set_control_par_str(get_ui_id($log_label),$CONTROL_PAR_TEXTLINE...\
        ,pgs_get_str_key_val(_log_msg))
      end if
      if (pgs_get_key_val(_log_flag,0)=2)
        pgs_set_key_val(_log_flag,0,0)
        set_control_par_str(get_ui_id($log_label),$CONTROL_PAR_TEXT,...\
        "log started")
      end if
    end on'''

    def __init__(self, l_type: object, path: str=None) -> None:
        self._type = l_type
        self._path = path
        if l_type is self.pgs:
            pgs_create_str_key('_log_msg')
            pgs_create_key('_log_flag', 1)
            pgs_set_key_val('_log_flag', 0, 2)
        if l_type is self.array:
            if not self._path:
                self._simple_log_init()
            else:
                self._log_with_path_init()
            self._log_count = kInt(name='_log_count')
            self._log_prev_count = kInt(name='_log_prev_count')

    def _simple_log_init(self):
        self._log_arr = kArrStr(name='_log_array', size=32768)

    def _log_with_path_init(self):
        postfix = ''
        postfix = '.nka'
        if self._path.endswith('.nka'):
            self._path = self._path[:-4]
        is_name = True
        name = list()
        path = list()
        for idx in range(len(self._path)):
            idx += 1
            char = self._path[-idx]
            if char in (r'/', r'\\', ':'):
                is_name = False
            if is_name:
                name.append(char)
            path.append(char)
        name.reverse()
        path.reverse()
        self._path = ''.join(path)
        self._path += postfix
        name = ''.join(name)
        self._log_arr = kArrStr(name=name, size=32768)

    def _log_arr_pers(self):
        Output().put('while(1=1)')
        with If(self._log_prev_count != self._log_count):
            check()
            if not self._path:
                save_array(self._log_arr, 1)
            else:
                save_array_str(self._log_arr, self._path)
        self._log_prev_count <<= self._log_count
        wait(200000)
        Output().put('end while')

    def put(self, *args, sep=' '):
        self._check_sep(sep)
        line = ''
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
        if self._type == self.pgs:
            Output().put(f'pgs_set_str_key_val(_log_msg, {line})')
            pgs_set_key_val('_log_flag', 0, 1)
        if self._type is self.array:
            var = self._log_arr[self._log_count]._get_compiled()
            Output().put(f'{var} := {line}')
            self._log_count <<= (self._log_count + 1) % 32768

    def _check_sep(self, sep):
        for char in sep:
            if char in ('\n', '\r', '\t', '\v'):
                raise AttributeError(
                    f'symbol {repr(char)} is not allowed')
