from collections import OrderedDict

from .native_types import kNone
from .native_types import kInt

# from k_built_ins import all_callbacks
from .k_built_ins import BuiltInFuncInt
from .k_built_ins import NI_ASYNC_ID
from .k_built_ins import InitCallback
from .k_built_ins import UiUpdateCallback
from .k_built_ins import UiControlCallback
from .k_built_ins import PgsCallback
from .k_built_ins import MidiCallback
from .k_built_ins import BuiltInIntVar
from .k_built_ins import ListenerCallback
from .k_built_ins import AsyncCompleteCallback

from .bi_notes_events import bEventParVar
from .bi_notes_events import bEventMark
# from k_built_ins import all_callbacks
# from k_built_ins import all_callbacks
# from k_built_ins import all_callbacks
# from k_built_ins import all_callbacks
# from k_built_ins import all_callbacks
# from k_built_ins import all_callbacks


class bMidiVar(BuiltInIntVar):
    pass


class bMidiCommand(BuiltInIntVar):
    pass


MIDI_COMMAND_NOTE_ON = bMidiCommand('MIDI_COMMAND_NOTE_ON',
                                    callbacks=(InitCallback,
                                               MidiCallback))
MIDI_COMMAND_POLY_AT = bMidiCommand('MIDI_COMMAND_POLY_AT',
                                    callbacks=(InitCallback,
                                               MidiCallback))
MIDI_COMMAND_CC = bMidiCommand('MIDI_COMMAND_CC',
                               callbacks=(InitCallback,
                                          MidiCallback))
MIDI_COMMAND_PROGRAM_CHANGE = bMidiCommand('MIDI_COMMAND_PROGRAM_CHANGE',
                                           callbacks=(InitCallback,
                                                      MidiCallback))
MIDI_COMMAND_MONO_AT = bMidiCommand('MIDI_COMMAND_MONO_AT',
                                    callbacks=(InitCallback,
                                               MidiCallback))
MIDI_COMMAND_PITCH_BEND = bMidiCommand('MIDI_COMMAND_PITCH_BEND',
                                       callbacks=(InitCallback,
                                                  MidiCallback))
MIDI_COMMAND_RPN = bMidiCommand('MIDI_COMMAND_RPN',
                                callbacks=(InitCallback,
                                           MidiCallback))
MIDI_COMMAND_NRPN = bMidiCommand('MIDI_COMMAND_NRPN',
                                 callbacks=(InitCallback,
                                            MidiCallback))
MIDI_BYTE_1 = bMidiVar('MIDI_BYTE_1',
                       callbacks=(InitCallback,
                                  MidiCallback))
MIDI_BYTE_2 = bMidiVar('MIDI_BYTE_2',
                       callbacks=(InitCallback,
                                  MidiCallback))
MIDI_COMMAND = bMidiVar('MIDI_COMMAND',
                        callbacks=(MidiCallback))
MIDI_CHANNEL = bMidiVar('MIDI_CHANNEL',
                        callbacks=(MidiCallback))

# MIDI_OBJECT_COMMANDS

# class MidiEvent: # TODO

#     def __init__(self, track, pos, command, byte1, byte2, idx):

#         self.track = track
#         self.pos = pos
#         self._command = command
#         self.byte1 = byte1
#         self.byte2 = byte2
#         self.idx = idx

#     @property
#     def command(self):
#         if not KSP.is_compiled():
#             return self._command.id
#         return self._command

#     @command.setter
#     def command(self, val):
#         self._command = val


# class MidiObject(metaclass=SingletonMeta):

#     def __init__(self):
#         self.buffer = list([None] * 1000000)
#         self.max_idx = 0
#         self.size = 0
#         self.num_tracks = 0

#     def insert_event(self, track, pos, command, byte1, byte2):
#         if track > self.num_tracks:
#             self.num_tracks = track
#         self.buffer[self.size] = MidiEvent(track, pos, command,
#                                            byte1, byte2)
#         self.max_idx += 1
#         self.size -= 1
#         if self.max_idx > self.size:
#             raise RuntimeError('midi buffer is overflow')
#         return self.max_idx - 1

#     def remove_event(self, idx):
#         obj = self.buffer[idx]
#         self.buffer[idx] = None
#         del obj

#     def reset(self):
#         for idx in range(self.max_idx + 1):
#             self.remove_event(idx)
#         self.size = 0

#     def get_next(self, track):

#     def get_next_at(self, track, pos):
#         for idx in range(self.max_idx + 1):
#             obj = self.buffer[idx]
#             if obj.pos > pos:
#                 if track == -1 or obj.track == track:
#                     return obj
#         return -1

#     def get_prev_at(self, track, pos):
#         for idx in range(self.max_idx + 1):
#             obj = self.buffer[self.max_idx - idx]
#             if obj.pos < pos:
#                 if track == -1 or obj.track == track:
#                     return obj
#         return -1


class MfInsertFile(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_insert_file',
                         args=OrderedDict(path=str,
                                          track_offset=int,
                                          position_offset=int,
                                          mode=int),
                         def_ret=NI_ASYNC_ID,
                         callbacks=(InitCallback,
                                    UiUpdateCallback,
                                    UiControlCallback,
                                    PgsCallback))

    def __call__(self, path: str, track_offset: int,
                 position_offset: int,
                 mode: int):
        '''inserts a MIDI file into the MIDI object.
        <path>
        the absolute path of the MIDI file, including the file name
        <track-offset>
        applies a track offset to the MIDI data
        <position-offset>
        applies a position offset, in ticks, to the MIDI data
        <mode>
        defines the mode of insertion:
        0: replace all existing events
        1: replace only overlapping
        Remarks
        • The loading of MIDI files with this command is asynchronous,
        so it is advised to use the async_complete callback to check the
        status of the load. However, the async_complete callback will
        not be called if this command is used in the init callback.
        • This command will pair Note On and Note Off events to a single
        Note On with a Note Length parameter. The Note Off events will
        be discarded.'''
        return super().__call__(path, track_offset,
                                position_offset, mode)


mf_insert_file = MfInsertFile().__call__


class MfSetExportArea(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_set_export_area',
                         args=OrderedDict(name=str,
                                          end_pos=int,
                                          start_track=int,
                                          end_track=int),
                         def_ret=1)

    def __call__(self, name: str, end_pos: int,
                 start_track: int,
                 end_track: int):
        '''defines the part of the MIDI object that will be exported
        when using a drag and drop area, or the save_midi_file() command.
        <name>
        sets the name of the exported file
        <start-pos>
        defines the start position (in ticks) of the export area.
        Use -1 to set this to the start of the MIDI object.
        <end-pos>
        defines the end position (in ticks) of the export area.
        Use -1 to set this to the end of the MIDI object.
        <start-track>
        defines the first track to be included in the export area.
        Use -1 to set this to the first track of the MIDI object.
        <end-track>
        defines the last track to be included in the export area.
        Use -1 to set this to the last track of the MIDI object.
        Remarks
        • If a start point is given a value greater than the end point,
        the values will be swapped.
        • When this command is executed, the events in the range are
        checked if they are valid MIDI commands. The command will return
        a value'''
        return super().__call__(name, end_pos,
                                start_track, end_track)


mf_set_export_area = MfSetExportArea().__call__


class MfSetBufferSize(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_set_buffer_size',
                         args=OrderedDict(size=int),
                         def_ret=NI_ASYNC_ID)

    def __call__(self, size: int):
        '''defines a number of inactive MIDI events, that can be activated
        and edited
        <size>
        the size of the MIDI object edit buffer
        Remarks
        • Using the mf_insert_event() and mf_remove_event() technically
        activate or deactivate events in the buffer.
        • It is not possible to insert MIDI events without first setting
        a buffer size
        • The maximum buffer size is 1,000,000 events (including both
        active and inactive events)
        • If this command is called outside of the init callback, it is
        asynchronous, and thus calls the async_complete callback.
        • Inserting a MIDI event will decrease the buffer size by one.
        Removing an event will increase it by one.
        • Inserting a MIDI file will not affect the buffer.'''
        return super().__call__(size)


mf_set_buffer_size = MfSetBufferSize().__call__


class MfSetBufferSize(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_set_buffer_size',
                         args=OrderedDict(size=int),
                         def_ret=NI_ASYNC_ID)

    def __call__(self, size: int):
        '''defines a number of inactive MIDI events, that can be activated
        and edited
        <size>
        the size of the MIDI object edit buffer
        Remarks
        • Using the mf_insert_event() and mf_remove_event() technically
        activate or deactivate events in the buffer.
        • It is not possible to insert MIDI events without first setting
        a buffer size
        • The maximum buffer size is 1,000,000 events (including both
        active and inactive events)
        • If this command is called outside of the init callback, it is
        asynchronous, and thus calls the async_complete callback.
        • Inserting a MIDI event will decrease the buffer size by one.
        Removing an event will increase it by one.
        • Inserting a MIDI file will not affect the buffer.'''
        return super().__call__(size)


mf_set_buffer_size = MfSetBufferSize().__call__


class MfGetBufferSize(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_buffer_size',
                         def_ret=1)

    def __call__(self):
        '''returns the size of the MIDI event buffer
        Remarks
        • The maximum buffer size is 1,000,000 events (including both
        active and inactive events)
        • Inserting a MIDI event will decrease the buffer size by one.
        Removing an event will increase it by one.'''
        return super().__call__()


mf_get_buffer_size = MfGetBufferSize().__call__


class MfReset(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_reset',
                         def_ret=NI_ASYNC_ID)

    def __call__(self):
        '''resets the MIDI object, sets the event buffer to zero, and
        removes all events
        Remarks
        • This command purges all MIDI data, use with caution
        • This command is also asynchronous, and thus calls the
        async_complete callback'''
        return super().__call__()


mf_reset = MfReset().__call__


class MfInsetEvent(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_insert_event',
                         args=OrderedDict(track=int,
                                          pos=int,
                                          command=bMidiCommand,
                                          byte1=int,
                                          byte2=int),
                         def_ret=1)

    def __call__(self, track: int, pos: int, command: bMidiCommand,
                 byte1: int,
                 byte2: int):
        '''activates an inactive MIDI event in the MIDI object.
        However, because the command and position are defined in this
        command, it can be considered as an insertion.
        <track>
        the track into which the MIDI event will be inserted
        <pos>
        the position at which the event will be inserted, in MIDI ticks
        <command>
        defines the command type of the MIDI event, can be one of the
        following:
        $MIDI_COMMAND_NOTE_ON
        $MIDI_COMMAND_POLY_AT
        $MIDI_COMMAND_CC
        $MIDI_COMMAND_PROGRAM_CHANGE
        $MIDI_COMMAND_MONO_AT
        $MIDI_COMMAND_PITCH_BEND
        <byte1>
        the first byte of the MIDI command
        <byte2>
        the second byte of the MIDI command
        Remarks
        • It is not possible to insert MIDI events without first setting
        an event buffer size with the mf_set_buffer_size() command
        • Using this command when the buffer is full
        (i.e. has a size of zero) will do nothing
        • You can retrieve the event ID of the inserted event in a
        variable by writing: <variable> := mf_insert_event
        <track>,<pos>,<command>,<byte1>,<byte2>)'''
        return super().__call__(track, pos, command, byte1, byte2)


mf_insert_event = MfInsetEvent().__call__


class MfRemoveEvent(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_remove_event',
                         args=OrderedDict(event_id=int),
                         def_ret=kNone())

    def __call__(self, event_id: int):
        '''deactivates an event in the MIDI object, effectively
        removing it
        <event-id>
        the ID of the event to be deactivated'''
        return super().__call__(event_id)


mf_remove_event = MfRemoveEvent().__call__


class MfSetEventPar(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_set_event_par',
                         args=OrderedDict(event_id=int,
                                          parameter=bEventParVar,
                                          value=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, parameter: bEventParVar, value: int):
        '''sets an event parameter
        <event-id>
        the ID of the event to be edited
        <parameter>
        the event parameter, either one of four freely assignable
        event parameter:
        $EVENT_PAR_0
        $EVENT_PAR_1
        $EVENT_PAR_2
        $EVENT_PAR_3
        or the "built-in" parameters of a MIDI event:
        $EVENT_PAR_MIDI_CHANNEL
        $EVENT_PAR_MIDI_COMMAND
        $EVENT_PAR_MIDI_BYTE_1
        $EVENT_PAR_MIDI_BYTE_2
        $EVENT_PAR_POS
        $EVENT_PAR_NOTE_LENGTH
        $EVENT_PAR_TRACK_NR
        <value>
        the value of the event parameter
        Remarks
        • You can control all events in the MIDI object by using the
        $ALL_EVENTS constant as the event ID.
        • You can access the currently selected event by using the
        $CURRENT_EVENT constant.
        • You can also control events by track, or group them with
        markers by using the by_track() and by_mark() commands.'''
        return super().__call__(event_id, parameter, value)


mf_set_event_par = MfSetEventPar().__call__


class MfGetEventPar(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_event_par',
                         args=OrderedDict(event_id=int,
                                          parameter=bEventParVar),
                         def_ret=kNone())

    def __call__(self, event_id: int, parameter: bEventParVar):
        '''returns the value of an event parameter
        <event-id>
        the ID of the event to be edited
        <parameter>
        the event parameter, either one of four freely assignable
        event parameter:
        $EVENT_PAR_0
        $EVENT_PAR_1
        $EVENT_PAR_2
        $EVENT_PAR_3
        or the "built-in" parameters of a MIDI event:
        $EVENT_PAR_MIDI_CHANNEL
        $EVENT_PAR_MIDI_COMMAND
        $EVENT_PAR_MIDI_BYTE_1
        $EVENT_PAR_MIDI_BYTE_2
        $EVENT_PAR_POS
        $EVENT_PAR_NOTE_LENGTH
        $EVENT_PAR_ID
        $EVENT_PAR_TRACK_NR'''
        return super().__call__(event_id, parameter)


mf_get_event_par = MfGetEventPar().__call__


class MfGetId(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_id',
                         def_ret=1)

    def __call__(self):
        '''returns the ID of the currently selected event
        (when usingthe navigation commands like mf_get_first(),
        and mf_get_next(), etc)'''
        return super().__call__()


mf_get_id = MfGetId().__call__


class MfSetMark(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_set_mark',
                         args=OrderedDict(event_id=int,
                                          mark=bEventMark,
                                          status=int),
                         def_ret=kNone())

    def __call__(self, event_id: int, mark: bEventMark, status: int):
        '''marks an event, so that you may groups events together
        and process that group quickly
        <event-id>
        the ID of the event to be marked
        <mark>
        the mark number. Use the constants $MARK_1 to $MARK_10
        <status>
        set this to 1 to mark an event or to 0 to unmark an event'''
        return super().__call__(event_id, mark, status)


mf_set_mark = MfSetMark().__call__


class MfGetMark(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_mark',
                         args=OrderedDict(event_id=int,
                                          mark=bEventMark),
                         def_ret=kNone())

    def __call__(self, event_id: int, mark: bEventMark):
        '''checks if an event is marked or not. Returns 1 if it is
        marked, or 0 if it is not.
        <event-id>
        the ID of the event to be edited
        <mark>
        the mark number. Use the constants $MARK_1 to $MARK_10'''
        return super().__call__(event_id, mark)


mf_get_mark = MfGetMark().__call__

# by_marks also is working for midi events


class MfByTrack(BuiltInFuncInt):

    def __init__(self):
        super().__init__('by_track',
                         args=OrderedDict(track_nr=int),
                         def_ret=1)

    def __call__(self, track_nr: int):
        '''can be used to group events by their track number
        <track>
        the track number of the events you wish to access'''
        return super().__call__(track_nr)


by_track = MfByTrack().__call__


class MfGetFirst(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_first',
                         args=OrderedDict(track_nr=int),
                         def_ret=1)

    def __call__(self, track_nr: int):
        '''moves the position marker to the first event in the MIDI track
        <track-index>
        the number of the track you want to edit. -1 refers to the
        whole file.'''
        return super().__call__(track_nr)


mf_get_first = MfGetFirst().__call__


class MfGetLast(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_last',
                         args=OrderedDict(track_nr=int),
                         def_ret=1)

    def __call__(self, track_nr: int):
        '''moves the position marker to the last event in the MIDI track
        <track-index>
        the number of the track you want to edit. -1 refers to the
        whole file.'''
        return super().__call__(track_nr)


mf_get_last = MfGetLast().__call__


class MfGetNext(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_next',
                         args=OrderedDict(track_nr=int),
                         def_ret=1)

    def __call__(self, track_nr: int):
        '''moves the position marker to the next event in the MIDI track
        <track-index>
        the number of the track you want to edit. -1 refers to the
        whole file.'''
        return super().__call__(track_nr)


mf_get_next = MfGetNext().__call__


class MfGetPrev(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_prev',
                         args=OrderedDict(track_nr=int),
                         def_ret=1)

    def __call__(self, track_nr: int):
        '''moves the position marker to the previous event in the
        MIDI track
        <track-index>
        the number of the track you want to edit. -1 refers to the
        whole file.'''
        return super().__call__(track_nr)


mf_get_prev = MfGetPrev().__call__


class MfGetNextAt(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_next_at',
                         args=OrderedDict(track_nr=int,
                                          pos=int),
                         def_ret=1)

    def __call__(self, track_nr: int, pos: int):
        '''moves the position marker to the next event in the MIDI
        track right after the defined position.
        <track-index>
        the number of the track you want to edit. -1 refers to
        the whole file.
        <pos>
        position in ticks'''
        return super().__call__(track_nr, pos)


mf_get_next_at = MfGetNextAt().__call__


class MfGetPrevAt(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_prev_at',
                         args=OrderedDict(track_nr=int,
                                          pos=int),
                         def_ret=1)

    def __call__(self, track_nr: int, pos: int):
        '''moves the position marker to the first event before
        the defined position
        <track-index>
        the number of the track you want to edit. -1 refers to
        the whole file.
        <pos>
        position in ticks'''
        return super().__call__(track_nr, pos)


mf_get_prev_at = MfGetPrevAt().__call__


class MfGetNumTracks(BuiltInFuncInt):

    def __init__(self):
        super().__init__('mf_get_num_tracks',
                         def_ret=1)

    def __call__(self):
        '''returns the ID of the currently selected event
        (when usingthe navigation commands like mf_get_first(),
        and mf_get_next(), etc)'''
        return super().__call__()


mf_get_num_tracks = MfGetNumTracks().__call__


class SetMidi(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_midi',
                         args=OrderedDict(channel=int,
                                          command=bMidiCommand,
                                          byte1=int,
                                          byte2=(int, kInt)),
                         callbacks=(UiControlCallback,
                                    InitCallback,
                                    UiUpdateCallback,
                                    ListenerCallback,
                                    AsyncCompleteCallback,
                                    MidiCallback),
                         def_ret=1)

    def __call__(self, channel: int, command: bMidiCommand,
                 byte1: int, byte2: int):
        '''create any type of MIDI event
        Remarks
        If you simply want to change the MIDI channel and/or any of
        the MIDI bytes, you can also use set_event_par().'''
        return super().__call__(channel, command, byte1, byte2)


set_midi = SetMidi().__call__
