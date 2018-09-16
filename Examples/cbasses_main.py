from pyksp.compiler import *
from pyksp.compiler.classic_builtins import *


script = kScript(kScript.clipboard, 'test_trem')

norm_rls_groups = [
    'CL_trem_rls_norm_ff',
    'OH_trem_rls_norm_ff',
    'S_trem_rls_norm_ff',
    'CL_trem_rls_norm_f',
    'OH_trem_rls_norm_f',
    'S_trem_rls_norm_f',
    'CL_trem_rls_norm_p',
    'OH_trem_rls_norm_p',
    'S_trem_rls_norm_p',
    'CL_trem_rls_norm_pp',
    'OH_trem_rls_norm_pp',
    'S_trem_rls_norm_pp'
]

sule_sus_groups = [
    'CL_trem_sus_sulE_ff',
    'OH_trem_sus_sulE_ff',
    'S_trem_sus_sulE_ff',
    'CL_trem_sus_sulE_f',
    'OH_trem_sus_sulE_f',
    'S_trem_sus_sulE_f',
    'CL_trem_sus_sulE_p',
    'OH_trem_sus_sulE_p',
    'S_trem_sus_sulE_p',
    'CL_trem_sus_sulE_pp',
    'OH_trem_sus_sulE_pp',
    'S_trem_sus_sulE_pp'
]
norm_sus_groups = [
    'CL_trem_sus_norm_ff',
    'OH_trem_sus_norm_ff',
    'S_trem_sus_norm_ff',
    'CL_trem_sus_norm_f',
    'OH_trem_sus_norm_f',
    'S_trem_sus_norm_f',
    'CL_trem_sus_norm_p',
    'OH_trem_sus_norm_p',
    'S_trem_sus_norm_p',
    'CL_trem_sus_norm_pp',
    'OH_trem_sus_norm_pp',
    'S_trem_sus_norm_pp'
]

sule_rls_groups = [
    'CL_trem_rls_sulE_ff',
    'OH_trem_rls_sulE_ff',
    'S_trem_rls_sulE_ff',
    'CL_trem_rls_sulE_f',
    'OH_trem_rls_sulE_f',
    'S_trem_rls_sulE_f',
    'CL_trem_rls_sulE_p',
    'OH_trem_rls_sulE_p',
    'S_trem_rls_sulE_p',
    'CL_trem_rls_sulE_pp',
    'OH_trem_rls_sulE_pp',
    'S_trem_rls_sulE_pp'
]

norm_diapasone = 34, 51
sulE_diapasone = 28, 40

kLog(kLog.pgs)

last_id = kInt(0, 'last_id')
curr_id = kInt(0, 'curr_id')


def main():
    rls = object()
    sus = object()

    message('')
    mw = kMainWindow(icon=False)
    set_ui_color(0x000000)
    cl_kn = kKnob(0, 1000000, 10000)
    cl_kn.text <<= 'Close'
    cl_kn.default <<= 630000
    oh_kn = kKnob(0, 1000000, 10000)
    oh_kn.text <<= 'OH'
    oh_kn.default <<= 630000
    s_kn = kKnob(0, 1000000, 10000)
    s_kn.text <<= 'Lead'
    s_kn.default <<= 630000

    norm_sus_grps_str = kArrStr(norm_sus_groups)
    norm_sus_grps_idx = kArrInt(size=len(norm_sus_groups),
                                name='norm_sus_grps_idx')
    norm_rls_grps_str = kArrStr(norm_rls_groups)
    norm_rls_grps_idx = kArrInt(size=len(norm_rls_groups),
                                name='norm_rls_grps_idx')

    sule_sus_grps_str = kArrStr(sule_sus_groups)
    sule_sus_grps_idx = kArrInt(size=len(sule_sus_groups),
                                name='sule_sus_grps_idx')
    sule_rls_grps_str = kArrStr(sule_rls_groups)
    sule_rls_grps_idx = kArrInt(size=len(sule_rls_groups),
                                name='sule_rls_grps_idx')
    with For(len(sule_sus_groups)) as seq:
        for idx in seq:
            norm_sus_grps_idx[idx] <<= find_group(norm_sus_grps_str[idx])
            sule_sus_grps_idx[idx] <<= find_group(sule_sus_grps_str[idx])
            norm_rls_grps_idx[idx] <<= find_group(norm_rls_grps_str[idx])
            sule_rls_grps_idx[idx] <<= find_group(sule_rls_grps_str[idx])

    def lvl_cb(control):
        """Callback of knobs.
        Set level of bus, respect to knob selected"""
        if control is cl_kn:
            bus = 0
        elif control is oh_kn:
            bus = 1
        elif control is s_kn:
            bus = 2
        set_engine_par(ENGINE_PAR_VOLUME, control.var, -
                       1, -1, NI_BUS_OFFSET + bus)
        control.label <<= get_engine_par_disp(
            ENGINE_PAR_VOLUME, -1, -1, NI_BUS_OFFSET + bus)
    for kn in (cl_kn, oh_kn, s_kn):
        kn.bound_callback(lvl_cb)

    sulE = kButton()
    sulE.text <<= 'sulE (KS - C0)'
    sulE_note = 24
    set_key_color(sulE_note, KEY_COLOR_LIME)
    set_key_name(sulE_note, 'sulE')
    last_id = kInt(0, 'last_id')
    curr_id = kInt(0, 'curr_id')

    def allow_groups(type):
        """Allow sulE or Norm groups depends on diapasone and callback."""
        if type is sus:
            sule_arr = sule_sus_grps_idx
            norm_arr = norm_sus_grps_idx
        else:
            sule_arr = sule_rls_grps_idx
            norm_arr = norm_rls_grps_idx
        with If(in_range(EVENT_NOTE, norm_diapasone[0], sulE_diapasone[1])):
            with Select(sulE.var):
                with Case(1):
                    check()
                    with For(arr=sule_arr) as seq:
                        for grp in seq:
                            allow_group(grp)
                with Case(0):
                    check()
                    with For(arr=norm_arr) as seq:
                        for grp in seq:
                            allow_group(grp)
        with Else():
            check()
            with For(len(norm_arr)) as seq:
                for idx in seq:
                    allow_group(norm_arr[idx])
                    allow_group(sule_arr[idx])

    @on.note
    def note_cb():
        """SulE keyswitch and legato logic"""
        ignore_event(EVENT_ID)
        disallow_group(ALL_GROUPS)

        with If(EVENT_NOTE == sulE_note):
            check()
            with If(EVENT_VELOCITY > 60):
                check()
                sulE.var <<= 1
            with Else():
                check()
                sulE.var <<= 0
        with If(in_range(EVENT_NOTE, sulE_diapasone[0], norm_diapasone[1])):
            check()
            allow_groups(sus)
            global last_id
            global curr_id
            curr_id <<= play_note(EVENT_NOTE, EVENT_VELOCITY, 0, -1)
            note_off(last_id)
            last_id <<= curr_id
            # <<= 0

    @on.release
    def release_cb():
        """Play release if the note released is last touched."""
        disallow_group(ALL_GROUPS)
        with If(EVENT_ID == last_id):
            check()
            logpr('EVENT_ID == last_id')
            allow_groups(rls)
            play_note(EVENT_NOTE, EVENT_VELOCITY, 0, 0)


script.main = main

script.compile()
