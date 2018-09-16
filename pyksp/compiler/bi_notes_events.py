from collections import OrderedDict

from k_built_ins import NoteCallback
from k_built_ins import BuiltInFuncInt
from k_built_ins import ReleaseCallback
from k_built_ins import ControllerCallback
from k_built_ins import BuiltInArrayInt
from k_built_ins import BuiltInIntVar
from k_built_ins import PolyAtCallback
from k_built_ins import RpnCallback


# from base_types import KspArray
from base_types import KspIntVar
from base_types import AstBase

from native_types import kNone
from native_types import kArrInt


class bEventMark(BuiltInIntVar):
    pass


MARK_1 = bEventMark('MARK_1')
MARK_2 = bEventMark('MARK_2')
MARK_3 = bEventMark('MARK_3')
MARK_4 = bEventMark('MARK_4')
MARK_5 = bEventMark('MARK_5')
MARK_6 = bEventMark('MARK_6')
MARK_7 = bEventMark('MARK_7')
MARK_8 = bEventMark('MARK_8')
MARK_9 = bEventMark('MARK_9')
MARK_10 = bEventMark('MARK_10')
MARK_11 = bEventMark('MARK_11')
MARK_12 = bEventMark('MARK_12')
MARK_13 = bEventMark('MARK_13')
MARK_14 = bEventMark('MARK_14')
MARK_15 = bEventMark('MARK_15')
MARK_16 = bEventMark('MARK_16')
MARK_17 = bEventMark('MARK_17')
MARK_18 = bEventMark('MARK_18')
MARK_19 = bEventMark('MARK_19')
MARK_20 = bEventMark('MARK_20')
MARK_21 = bEventMark('MARK_21')
MARK_22 = bEventMark('MARK_22')
MARK_23 = bEventMark('MARK_23')
MARK_24 = bEventMark('MARK_24')
MARK_25 = bEventMark('MARK_25')
MARK_26 = bEventMark('MARK_26')
MARK_27 = bEventMark('MARK_27')
MARK_28 = bEventMark('MARK_28')

CC = BuiltInArrayInt('CC', 128)
CC_TOUCHED = BuiltInArrayInt('CC_TOUCHED', 128,
                             (ControllerCallback,))
CC_NUM = BuiltInIntVar('CC_NUM',
                       (ControllerCallback,))
EVENT_ID = BuiltInIntVar('EVENT_ID',
                         callbacks=(NoteCallback, ReleaseCallback))
EVENT_NOTE = BuiltInIntVar('EVENT_NOTE',
                           callbacks=(NoteCallback, ReleaseCallback))
EVENT_VELOCITY = BuiltInIntVar('EVENT_VELOCITY',
                               callbacks=(NoteCallback, ReleaseCallback))
CURRENT_EVENT = BuiltInIntVar('CURRENT_EVENT')


class bEventParVar(BuiltInIntVar):
    pass


EVENT_PAR_0 = bEventParVar('EVENT_PAR_0')
EVENT_PAR_1 = bEventParVar('EVENT_PAR_1')
EVENT_PAR_2 = bEventParVar('EVENT_PAR_2')
EVENT_PAR_3 = bEventParVar('EVENT_PAR_3')
EVENT_PAR_VOLUME = bEventParVar('EVENT_PAR_VOLUME')
EVENT_PAR_PAN = bEventParVar('EVENT_PAR_PAN')
EVENT_PAR_TUNE = bEventParVar('EVENT_PAR_TUNE')
EVENT_PAR_NOTE = bEventParVar('EVENT_PAR_NOTE')
EVENT_PAR_VELOCITY = bEventParVar('EVENT_PAR_VELOCITY')
EVENT_PAR_ALLOW_GROUP = bEventParVar('EVENT_PAR_ALLOW_GROUP')
EVENT_PAR_SOURCE = bEventParVar('EVENT_PAR_SOURCE')
EVENT_PAR_PLAY_POS = bEventParVar('EVENT_PAR_PLAY_POS')
EVENT_PAR_ZONE_ID = bEventParVar('EVENT_PAR_ZONE_ID')
EVENT_PAR_MIDI_CHANNEL = bEventParVar('EVENT_PAR_MIDI_CHANNEL')
EVENT_PAR_MIDI_COMMAND = bEventParVar('EVENT_PAR_MIDI_COMMAND')
EVENT_PAR_MIDI_BYTE_1 = bEventParVar('EVENT_PAR_MIDI_BYTE_1')
EVENT_PAR_MIDI_BYTE_2 = bEventParVar('EVENT_PAR_MIDI_BYTE_2')
EVENT_PAR_POS = bEventParVar('EVENT_PAR_POS')
EVENT_PAR_NOTE_LENGTH = bEventParVar('EVENT_PAR_NOTE_LENGTH')
EVENT_PAR_ID = bEventParVar('EVENT_PAR_ID')
EVENT_PAR_TRACK_NR = bEventParVar('EVENT_PAR_TRACK_NR')


class bEventStatusVar(BuiltInIntVar):
    pass


EVENT_STATUS_INACTIVE = bEventStatusVar('EVENT_STATUS_INACTIVE')
EVENT_STATUS_NOTE_QUEUE = bEventStatusVar('EVENT_STATUS_NOTE_QUEUE')
EVENT_STATUS_MIDI_QUEUE = bEventStatusVar('EVENT_STATUS_MIDI_QUEUE')

GROUPS_AFFECTED = BuiltInArrayInt('GROUPS_AFFECTED', 700,
                                  callbacks=(NoteCallback,
                                             ReleaseCallback))
NOTE_HELD = BuiltInIntVar('NOTE_HELD', callbacks=(NoteCallback,
                                                  ReleaseCallback))
POLY_AT = BuiltInArrayInt('POLY_AT', 128, callbacks=(PolyAtCallback,))
POLY_AT_NUM = BuiltInIntVar('POLY_AT_NUM', callbacks=(PolyAtCallback,))
RPN_ADDRESS = BuiltInIntVar('RPN_ADDRESS', callbacks=(RpnCallback,))
RPN_VALUE = BuiltInIntVar('RPN_VALUE', callbacks=(RpnCallback,))
VCC_MONO_AT = BuiltInIntVar('VCC_MONO_AT')
VCC_PITCH_BEND = BuiltInIntVar('VCC_PITCH_BEND')


class NoteOff(BuiltInFuncInt):

    def __init__(self):
        super().__init__('note_off',
                         args=OrderedDict(note_id=int),
                         def_ret=kNone())

    def __call__(self, note_id=int):
        '''send a note off message to a specific note
        <ID-number>
        the ID number of the note event
        Remarks
        • note_off() is equivalent to releasing a key, thus it will always
        trigger a release callback as well as the release portion of a
        volume envelope. Notice the difference between note_off() and
        fade_out(), since fade_out() works on a voice level'''
        return super().__call__(note_id)

    # def calculate(self, *args):
    #     return self._def_ret


note_off = NoteOff().__call__


class PlayNote(BuiltInFuncInt):

    def __init__(self):
        super().__init__('play_note',
                         args=OrderedDict(
                             note=(int, KspIntVar, AstBase),
                             velocity=(int, KspIntVar, AstBase),
                             sample_offset=(
                                 int, KspIntVar, AstBase),
                             duration=(int, KspIntVar, AstBase)),
                         def_ret=1)

    def __call__(self, note=int, velocity=int,
                 sample_offset=int, duration=int):
        '''generate a MIDI note, i.e. generate a note on message followed
        by a note off message
        <note-number>
        the note number to be generated (0 - 127)
        <velocity>
        velocity of the generated note (1 - 127)
        <sample-offset>
        sample offset in microseconds
        <duration>
        length of the generated note in microseconds
        this parameter also accepts two special values:
        -1: releasing the note which started the callback stops the sample
        0: the entire sample is played
        Remarks
        • In DFD mode, the sample offset is dependent on the Sample Mod
        (S.Mod) value of the respective zones. Sample offset value greater
        than the zone's S.Mod setting will be ignored and no sample offset
        will be applied.
        • You can retrieve the event ID of the played note in a variable
        by writing: <variable> := /
            play_note(<note>,<velocity>,<sample-offset>,<duration>)'''
        return super().__call__(note, velocity,
                                sample_offset, duration)

    # def calculate(self, *args):
    #     return self._def_ret


play_note = PlayNote().__call__


class SetController(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_controller',
                         args=OrderedDict(controller=int, value=int),
                         def_ret=kNone())

    def __call__(self, controller=int, value=int):
        '''send a MIDI CC, pitchbend or channel pressure value
        <controller>
        this parameter sets the type and in the case of MIDI CCs the
        CC number:
        • a number from 0 to 127 designates a MIDI CC number
        • $VCC_PITCH_BEND indicates Pitchbend
        • $VCC_MONO_AT indicates Channel Pressure (monophonic aftertouch)
        <value>
        the value of the specified controller
        MIDI CC and channel pressure values go from 0 to 127
        PitchBend values go from -8192 to 8191
        Remarks
        • set_controller() should not be used within an init callback.'''
        CC.set_value(controller, value)
        return super().__call__(controller, value)

    # def calculate(self, *args):
    #     return self._def_ret


set_controller = SetController().__call__


class SetRpn(BuiltInFuncInt):

    def __init__(self, name: str):
        super().__init__(name,
                         args=OrderedDict(address=int, value=int),
                         def_ret=kNone())

    def __call__(self, address=int, value=int):
        '''<address>
        the rpn or nrpn address (0 - 16383)
        <value>
        the value of the rpn or nrpn message (0 - 16383)'''
        RPN_ADDRESS.set_value(address)
        RPN_VALUE.set_value(value)
        return super().__call__(address, value)


set_rpn = SetRpn('set_rpn').__call__
set_nrpn = SetRpn('set_nrpn').__call__


class SetSnapshotType(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_snapshot_type',
                         args=OrderedDict(s_type=int),
                         def_ret=kNone())

    def __call__(self, s_type):
        '''<type>
        the available types are:
        0: the init callback will always be executed upon snapshot change,
        afterwards the on persistence_changed callback will be executed
        (default behavior)
        1: the init callback will not be executed upon loading a snapshot,
        only the on persistence_callback will be executed'''
        return super().__call__(s_type)


set_snapshot_type = SetSnapshotType().__call__


class ByMarks(BuiltInFuncInt):

    def __init__(self):
        super().__init__('by_marks',
                         args=OrderedDict(mark=bEventMark),
                         def_ret=kNone())

    def __call__(self, bit_mark):
        '''a user defined group of events (or event IDs)
        TODO (nothing happens with event till now)'''
        return super().__call__(bit_mark)


by_marks = ByMarks().__call__


class ChangeNote(BuiltInFuncInt):

    def __init__(self):
        super().__init__('change_note',
                         args=OrderedDict(event_id=int, note_nr=int),
                         def_ret=kNone(),
                         callbacks=(NoteCallback,))

    def __call__(self, event_id, note_nr):
        '''change the note number of a specific note event
        Remarks
        • change_note()is only allowed in the note callback and only
        works before the first wait() statement. If the voice is already
        running, only the value of the variable changes.
        • once the note number of a particular note event is changed,
        it becomes the new $EVENT_NOTE
        • it is not possible to address events via event groups
        like $ALL_EVENTS'''
        return super().__call__(event_id, note_nr)


change_note = ChangeNote().__call__


class ChangeVelo(BuiltInFuncInt):

    def __init__(self):
        super().__init__('change_velo',
                         args=OrderedDict(event_id=int, note_nr=int),
                         def_ret=kNone(),
                         callbacks=(NoteCallback,))

    def __call__(self, event_id, note_nr):
        '''change the note number of a specific note event
        Remarks
        • change_velo()is only allowed in the note callback and only
        works before the first wait() statement. If the voice is already
        running, only the value of the variable changes.
        • once the note number of a particular note event is changed,
        it becomes the new $EVENT_NOTE
        • it is not possible to address events via event groups
        like $ALL_EVENTS'''
        return super().__call__(event_id, note_nr)


change_velo = ChangeVelo().__call__


class ChangePan(BuiltInFuncInt):

    def __init__(self):
        super().__init__('change_pan',
                         args=OrderedDict(event_id=int,
                                          panorama=int,
                                          relative_bit=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, panorama: int, relative_bit: int):
        '''change the pan position of a specific note event
        <ID-number>
        the ID number of the note event to be changed
        <panorama>
        the pan position of the note event, from -1000 (left) to 1000
        (right)
        <relative-bit>
        If the relative bit is set to 0, the amount is absolute, i.e. the
        amount, overwrites any previous set values of that event.
        If set to 1, the amount is relative to the actual value of the
        event.
        The different implications are only relevant with more than one
        change_pan() statement applied to the same event.
        Remarks
        • change_pan()works on a note event level and does not change any
        panorama settings in the instrument itself. It is also not related
        to any MIDI modulations regarding panorama.'''
        return super().__call__(event_id, panorama, relative_bit)


change_pan = ChangePan().__call__


class ChangeTune(BuiltInFuncInt):

    def __init__(self):
        super().__init__('change_tune',
                         args=OrderedDict(event_id=int,
                                          tune=int,
                                          relative_bit=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, tune: int, relative_bit: int):
        '''change the pan position of a specific note event
        <ID-number>
        the ID number of the note event to be changed
        <tune>
        the pan position of the note event, from -1000 (left) to 1000
        (right)
        <relative-bit>
        If the relative bit is set to 0, the amount is absolute, i.e. the
        amount, overwrites any previous set values of that event.
        If set to 1, the amount is relative to the actual value of the
        event.
        The different implications are only relevant with more than one
        change_tune() statement applied to the same event.
        Remarks
        • change_tune()works on a note event level and does not change any
        tune settings in the instrument itself. It is also not related
        to any MIDI modulations regarding tune.'''
        return super().__call__(event_id, tune, relative_bit)


change_tune = ChangeTune().__call__


class ChangeVol(BuiltInFuncInt):

    def __init__(self):
        super().__init__('change_vol',
                         args=OrderedDict(event_id=int,
                                          vol=int,
                                          relative_bit=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, vol: int, relative_bit: int):
        '''change the pan position of a specific note event
        <ID-number>
        the ID number of the note event to be changed
        <vol>
        the pan position of the note event, from -1000 (left) to 1000
        (right)
        <relative-bit>
        If the relative bit is set to 0, the amount is absolute, i.e. the
        amount, overwrites any previous set values of that event.
        If set to 1, the amount is relative to the actual value of the
        event.
        The different implications are only relevant with more than one
        change_vol() statement applied to the same event.
        Remarks
        • change_vol()works on a note event level and does not change any
        vol settings in the instrument itself. It is also not related
        to any MIDI modulations regarding vol.'''
        return super().__call__(event_id, vol, relative_bit)


change_vol = ChangeVol().__call__


class DeleteEventMark(BuiltInFuncInt):

    def __init__(self):
        super().__init__('delete_event_mark',
                         args=OrderedDict(event_id=int,
                                          bit_mark=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, bit_mark: int):
        '''delete an event mark, i.e. ungroup the specified event
        from an event group
        <ID-number>
        the ID number of the event to be ungrouped
        <bit-mark>
        here you can enter one of 28 marks from $MARK_1 to $MARK_28 which
        is assigned to the event.'''
        return super().__call__(event_id, bit_mark)


delete_event_mark = DeleteEventMark().__call__


class EventStatus(BuiltInFuncInt):

    def __init__(self):
        super().__init__('event_status',
                         args=OrderedDict(event_id=int),
                         def_ret=kNone())

    def __call__(self, event_id: int):
        '''retrieve the status of a particular note event (or MIDI event
        in the multi script)
        The note can either be active, then this function returns
        $EVENT_STATUS_NOTE_QUEUE (or $EVENT_STATUS_MIDI_QUEUE in the
        multi script)
        or inactive, then the function returns
        $EVENT_STATUS_INACTIVE
        Remarks
        event_status() can be used to find out if a note event is still
        "alive" or not.'''
        return super().__call__(event_id)


event_status = EventStatus().__call__


class FadeIn(BuiltInFuncInt):

    def __init__(self):
        super().__init__('fade_in',
                         args=OrderedDict(event_id=int, fade_time=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, fade_time: int):
        '''perform a fade-in for a specific note event
        <ID-number>
        the ID number of the note event to be faded in
        <fade-time>
        the fade-in time in microseconds'''
        return super().__call__(event_id, fade_time)


fade_in = FadeIn().__call__


class FadeOuut(BuiltInFuncInt):

    def __init__(self):
        super().__init__('fade_in',
                         args=OrderedDict(event_id=int, fade_time=int,
                                          stop_voice=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, fade_time: int,
                 stop_voice: int):
        '''perform a fade-out for a specific note event
        <ID-number>
        the ID number of the note event to be faded in
        <fade-time>
        the fade-in time in microseconds
        <stop_voice>
        If set to 1, the voice is stopped after the fade out.
        If set to 0, the voice will still be running after the fade out'''
        return super().__call__(event_id, fade_time, stop_voice)


fade_in = FadeOuut().__call__


class GetEventIds(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_event_ids',
                         args=OrderedDict(dest_array=kArrInt))

    def __call__(self, dest_array: kArrInt):
        '''fills the specified array with all active event IDs.
        The command overwrites all existing values as long as there are
        events and writes 0 if no events are active anymore.
        <dest_array>
        array to be filled with active event IDs'''
        return super().__call__(dest_array)

    def calculate(self, dest_array):
        for idx, item in enumerate(dest_array.iter_runtime()):
            if idx < 7:
                item._set_runtime(idx)
            else:
                item._set_runtime(0)
        return kNone()


get_event_ids = GetEventIds().__call__


class GetEventPar(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_event_par',
                         args=OrderedDict(event_id=int,
                                          parameter=bEventParVar),
                         def_ret=kNone())

    def __call__(self, event_id: int, parameter: bEventParVar):
        '''return the value of a specific event parameter of the specified
        event
        <ID-number>
        the ID number of the event
        <parameter>
        the event parameter, either one of four freely assignable event
        parameter:
        $EVENT_PAR_0
        $EVENT_PAR_1
        $EVENT_PAR_2
        $EVENT_PAR_3
        or the "built-in" parameters of a note event:
        $EVENT_PAR_VOLUME
        $EVENT_PAR_PAN
        $EVENT_PAR_TUNE
        $EVENT_PAR_NOTE
        $EVENT_PAR_VELOCITY
        $EVENT_PAR_SOURCE
        $EVENT_PAR_PLAY_POS
        $EVENT_PAR_ZONE_ID (use with caution, see below)
        Remarks
        A note event always carries certain information like the note
        number, the played velocity, but also Volume, Pan and Tune. With
        set_event_par(), you can set either these parameters or use the
        freely assignable parameters like $EVENT_PAR_0. This is especially
        useful when chaining scripts, i.e. set an event parameter for an
        event in slot 1, then retrieve this information in slot 2 by using
        get_event_par().'''
        return super().__call__(event_id, parameter)


get_event_par = GetEventPar().__call__


class GetEventParArr(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_event_par_arr',
                         args=OrderedDict(event_id=int,
                                          parameter=bEventParVar,
                                          group_idx=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, parameter: bEventParVar,
                 group_idx: int):
        '''special form of get_event_par(), used to retrieve the group
        allow state of the specified event
        <ID-number>
        the ID number of the note event
        <parameter>
        in this case, only $EVENT_PAR_ALLOW_GROUP
        <group-index>
        the index of the group for retrieving the specified note's group
        allow state
        Remarks
        • get_event_par_arr() is a special form (or to be more precise,
        it's the array variant) of get_event_par(). It is used to retrieve
        the allow state of a specific event. If will return 1, if the
        specified group is allowed and 0 if it's disallowed.'''
        return super().__call__(event_id, parameter, group_idx)


get_event_par_arr = GetEventParArr().__call__


class SetEventPar(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_event_par',
                         args=OrderedDict(event_id=int,
                                          parameter=bEventParVar,
                                          value=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, parameter: bEventParVar,
                 value: int):
        '''assign a parameter to a specific event
        <ID-number>
        the ID number of the event
        <parameter>
        the event parameter, either one of four freely assignable event
        parameter:
        $EVENT_PAR_0
        $EVENT_PAR_1
        $EVENT_PAR_2
        $EVENT_PAR_3
        or the "built-in" parameters of a note event:
        $EVENT_PAR_VOLUME
        $EVENT_PAR_PAN
        $EVENT_PAR_TUNE
        $EVENT_PAR_NOTE
        $EVENT_PAR_VELOCITY
        <value>
        the value of the event parameter
        Remarks
        A note event always "carries" certain information like the note
        number, the played velocity, but also Volume, Pan and Tune.
        With set_event_par(), you can set either these parameters or use
        the freely assignable parameters like $EVENT_PAR_0. This is
        especially useful when chaining scripts, i.e. set an event
        parameter for an event in slot 1, then retrieve this information
        in slot 2 by using get_event_par().
        The event parameters are not influenced by the system scripts
        anymore.'''
        return super().__call__(event_id, parameter, value)


set_event_par = SetEventPar().__call__


class SetEventParArr(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_event_par_arr',
                         args=OrderedDict(event_id=int,
                                          parameter=bEventParVar,
                                          value=int,
                                          group_idx=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, parameter: bEventParVar,
                 value: int, group_idx: int):
        '''special form of set_event_par(), used to set the group allow
        state of the specified event
        <ID-number>
        the ID number of the note event
        <parameter>
        in this case, only $EVENT_PAR_ALLOW_GROUP can be used
        <value>
        If set to 1, the group set with <groupindex> will be allowed for
        the event.
        If set to 0, the group set with <groupindex> will be disallowed
        for the event.
        <group-index>
        the index of the group for changing the specified note's group
        allow state
        Remarks
        • set_event_par_arr() is a special form (or to be more precise,
        it's the array variant) of set_event_par(). It is used to set the
        allow state of a specific event.'''
        return super().__call__(event_id, parameter, value, group_idx)


set_event_par_arr = SetEventParArr().__call__


class IgnoreEvent(BuiltInFuncInt):

    def __init__(self):
        super().__init__('ignore_event',
                         args=OrderedDict(event_id=int),
                         def_ret=kNone())

    def __call__(self, event_id: int):
        '''ignore a note event in a note on or note off callback
        Remarks
        • If you ignore an event, any volume, tune or pan information is
        lost. You can however retrieve this infomation with
        get_event_par(), see the two examples below.
        • ignore_event() is a very "strong" command. Always check if you
        can get the same results with the various change_xxx() commands
        without having to ignore the event.'''
        return super().__call__(event_id)


ignore_event = IgnoreEvent().__call__


class SetEventMark(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_event_mark',
                         args=OrderedDict(event_id=int,
                                          bit_mark=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, bit_mark: int):
        '''assign the specified event to a specific event group
        <ID-number>
        the ID number of the event to be grouped
        <bit-mark>
        here you can enter one of 28 marks from $MARK_1 to $MARK_28 which
        is assigned to the event. You can also assign more than one mark
        to a single event, either by typing the command or by using the
        operator +.
        Remarks
        When dealing with commands that deal with event IDs, you can
        group events by using by_marks(<bit-mark>) instead of the
        individual ID, since the program needs to know that you
        want to address marks and not IDs.'''
        return super().__call__(event_id, bit_mark)


set_event_mark = SetEventMark().__call__


class ResetRlsTriggCount(BuiltInFuncInt):

    def __init__(self):
        super().__init__('reset_rls_trig_counter',
                         args=OrderedDict(note_nr=int),
                         def_ret=kNone())

    def __call__(self, note_nr: int):
        '''resets the release trigger counter
        (used by the release trigger system script)'''
        return super().__call__(note_nr)


reset_rls_trig_counter = ResetRlsTriggCount().__call__


class WillNeverTerminate(BuiltInFuncInt):

    def __init__(self):
        super().__init__('will_never_terminate',
                         args=OrderedDict(event_id=int),
                         def_ret=kNone())

    def __call__(self, event_id: int):
        '''tells the script engine that this event will never be finished
        (used by the release trigger system script)'''
        return super().__call__(event_id)


will_never_terminate = WillNeverTerminate().__call__
