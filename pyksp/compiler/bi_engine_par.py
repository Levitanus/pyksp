from collections import OrderedDict

from .abstract import KSP
from .abstract import SingletonMeta
# from .k_built_ins import bEngineParVar
from .k_built_ins import BuiltInFuncInt
from .k_built_ins import BuiltInFuncStr
from .k_built_ins import get_runtime_val
from .k_built_ins import bTmProVar
from .native_types import kNone
from .k_built_ins import BuiltInIntVar
# from .k_built_ins import PgsCallback
# ENGINE_PAR_COMMANDS


class bEngineParVar(BuiltInIntVar):
    pass


ENGINE_PAR_VOLUME = bEngineParVar('ENGINE_PAR_VOLUME')
ENGINE_PAR_PAN = bEngineParVar('ENGINE_PAR_PAN')
ENGINE_PAR_TUNE = bEngineParVar('ENGINE_PAR_TUNE')


ENGINE_PAR_SMOOTH = bEngineParVar('ENGINE_PAR_SMOOTH')
ENGINE_PAR_FORMANT = bEngineParVar('ENGINE_PAR_FORMANT')
ENGINE_PAR_SPEED = bEngineParVar('ENGINE_PAR_SPEED')
ENGINE_PAR_GRAIN_LENGTH = bEngineParVar('ENGINE_PAR_GRAIN_LENGTH')
ENGINE_PAR_SLICE_ATTACK = bEngineParVar('ENGINE_PAR_SLICE_ATTACK')
ENGINE_PAR_SLICE_RELEASE = bEngineParVar('ENGINE_PAR_SLICE_RELEASE')
ENGINE_PAR_TRANSIENT_SIZE = bEngineParVar('ENGINE_PAR_TRANSIENT_SIZE')
ENGINE_PAR_ENVELOPE_ORDER = bEngineParVar('ENGINE_PAR_ENVELOPE_ORDER')
ENGINE_PAR_FORMANT_SHIFT = bEngineParVar('ENGINE_PAR_FORMANT_SHIFT')
ENGINE_PAR_SPEED_UNIT = bEngineParVar('ENGINE_PAR_SPEED_UNIT')

ENGINE_PAR_OUTPUT_CHANNEL = bEngineParVar('ENGINE_PAR_OUTPUT_CHANNEL')
NI_BUS_OFFSET = bEngineParVar('NI_BUS_OFFSET')
ENGINE_PAR_EFFECT_BYPASS = bEngineParVar('ENGINE_PAR_EFFECT_BYPASS')
ENGINE_PAR_INSERT_EFFECT_OUTPUT_GAIN = bEngineParVar(
    'ENGINE_PAR_INSERT_EFFECT_OUTPUT_GAIN')

ENGINE_PAR_RELEASE_TRIGGER = bEngineParVar(
    'ENGINE_PAR_RELEASE_TRIGGER')

ENGINE_PAR_THRESHOLD = bEngineParVar('ENGINE_PAR_THRESHOLD')
ENGINE_PAR_RATIO = bEngineParVar('ENGINE_PAR_RATIO')
ENGINE_PAR_COMP_ATTACK = bEngineParVar('ENGINE_PAR_COMP_ATTACK')
ENGINE_PAR_COMP_DECAY = bEngineParVar('ENGINE_PAR_COMP_DECAY')


ENGINE_PAR_LIM_IN_GAIN = bEngineParVar(
    'ENGINE_PAR_LIM_IN_GAIN')
ENGINE_PAR_LIM_RELEASE = bEngineParVar(
    'ENGINE_PAR_LIM_RELEASE')
ENGINE_PAR_SP_OFFSET_DISTANCE = bEngineParVar(
    'ENGINE_PAR_SP_OFFSET_DISTANCE')
ENGINE_PAR_SP_OFFSET_AZIMUTH = bEngineParVar(
    'ENGINE_PAR_SP_OFFSET_AZIMUTH')
ENGINE_PAR_SP_OFFSET_X = bEngineParVar(
    'ENGINE_PAR_SP_OFFSET_X')
ENGINE_PAR_SP_OFFSET_Y = bEngineParVar(
    'ENGINE_PAR_SP_OFFSET_Y')
ENGINE_PAR_SP_LFE_VOLUME = bEngineParVar(
    'ENGINE_PAR_SP_LFE_VOLUME')
ENGINE_PAR_SP_SIZE = bEngineParVar(
    'ENGINE_PAR_SP_SIZE')
ENGINE_PAR_SP_DIVERGENCE = bEngineParVar(
    'ENGINE_PAR_SP_DIVERGENCE')
ENGINE_PAR_SHAPE = bEngineParVar(
    'ENGINE_PAR_SHAPE')
ENGINE_PAR_BITS = bEngineParVar(
    'ENGINE_PAR_BITS')
ENGINE_PAR_FREQUENCY = bEngineParVar(
    'ENGINE_PAR_FREQUENCY')
ENGINE_PAR_NOISELEVEL = bEngineParVar(
    'ENGINE_PAR_NOISELEVEL')
ENGINE_PAR_NOISECOLOR = bEngineParVar(
    'ENGINE_PAR_NOISECOLOR')
ENGINE_PAR_STEREO = bEngineParVar(
    'ENGINE_PAR_STEREO')
ENGINE_PAR_STEREO_PAN = bEngineParVar(
    'ENGINE_PAR_STEREO_PAN')
ENGINE_PAR_DRIVE = bEngineParVar(
    'ENGINE_PAR_DRIVE')
ENGINE_PAR_DAMPING = bEngineParVar(
    'ENGINE_PAR_DAMPING')
ENGINE_PAR_SENDLEVEL_0 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_0')
ENGINE_PAR_SENDLEVEL_1 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_1')
ENGINE_PAR_SENDLEVEL_2 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_2')
ENGINE_PAR_SENDLEVEL_3 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_3')
ENGINE_PAR_SENDLEVEL_4 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_4')
ENGINE_PAR_SENDLEVEL_5 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_5')
ENGINE_PAR_SENDLEVEL_6 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_6')
ENGINE_PAR_SENDLEVEL_7 = bEngineParVar(
    'ENGINE_PAR_SENDLEVEL_7')
ENGINE_PAR_SK_TONE = bEngineParVar(
    'ENGINE_PAR_SK_TONE')
ENGINE_PAR_SK_DRIVE = bEngineParVar(
    'ENGINE_PAR_SK_DRIVE')
ENGINE_PAR_SK_BASS = bEngineParVar(
    'ENGINE_PAR_SK_BASS')
ENGINE_PAR_SK_BRIGHT = bEngineParVar(
    'ENGINE_PAR_SK_BRIGHT')
ENGINE_PAR_SK_MIX = bEngineParVar(
    'ENGINE_PAR_SK_MIX')
ENGINE_PAR_RT_SPEED = bEngineParVar(
    'ENGINE_PAR_RT_SPEED')
ENGINE_PAR_RT_BALANCE = bEngineParVar(
    'ENGINE_PAR_RT_BALANCE')
ENGINE_PAR_RT_ACCEL_HI = bEngineParVar(
    'ENGINE_PAR_RT_ACCEL_HI')
ENGINE_PAR_RT_ACCEL_LO = bEngineParVar(
    'ENGINE_PAR_RT_ACCEL_LO')
ENGINE_PAR_RT_DISTANCE = bEngineParVar(
    'ENGINE_PAR_RT_DISTANCE')
ENGINE_PAR_RT_MIX = bEngineParVar(
    'ENGINE_PAR_RT_MIX')
ENGINE_PAR_TW_VOLUME = bEngineParVar(
    'ENGINE_PAR_TW_VOLUME')
ENGINE_PAR_TW_TREBLE = bEngineParVar(
    'ENGINE_PAR_TW_TREBLE')
ENGINE_PAR_TW_MID = bEngineParVar(
    'ENGINE_PAR_TW_MID')
ENGINE_PAR_TW_BASS = bEngineParVar(
    'ENGINE_PAR_TW_BASS')
ENGINE_PAR_TW_BRIGHT = bEngineParVar(
    'ENGINE_PAR_TW_BRIGHT')
ENGINE_PAR_TW_MONO = bEngineParVar(
    'ENGINE_PAR_TW_MONO')
ENGINE_PAR_CB_SIZE = bEngineParVar(
    'ENGINE_PAR_CB_SIZE')
ENGINE_PAR_CB_AIR = bEngineParVar(
    'ENGINE_PAR_CB_AIR')
ENGINE_PAR_CB_TREBLE = bEngineParVar(
    'ENGINE_PAR_CB_TREBLE')
ENGINE_PAR_CB_BASS = bEngineParVar(
    'ENGINE_PAR_CB_BASS')
ENGINE_PAR_CABINET_TYPE = bEngineParVar(
    'ENGINE_PAR_CABINET_TYPE')
ENGINE_PAR_EXP_FILTER_MORPH = bEngineParVar(
    'ENGINE_PAR_EXP_FILTER_MORPH')
ENGINE_PAR_EXP_FILTER_AMOUNT = bEngineParVar(
    'ENGINE_PAR_EXP_FILTER_AMOUNT')
ENGINE_PAR_TP_GAIN = bEngineParVar(
    'ENGINE_PAR_TP_GAIN')
ENGINE_PAR_TP_WARMTH = bEngineParVar(
    'ENGINE_PAR_TP_WARMTH')
ENGINE_PAR_TP_HF_ROLLOFF = bEngineParVar(
    'ENGINE_PAR_TP_HF_ROLLOFF')
ENGINE_PAR_TP_QUALITY = bEngineParVar(
    'ENGINE_PAR_TP_QUALITY')
ENGINE_PAR_TR_INPUT = bEngineParVar(
    'ENGINE_PAR_TR_INPUT')
ENGINE_PAR_TR_ATTACK = bEngineParVar(
    'ENGINE_PAR_TR_ATTACK')
ENGINE_PAR_TR_SUSTAIN = bEngineParVar(
    'ENGINE_PAR_TR_SUSTAIN')
ENGINE_PAR_TR_SMOOTH = bEngineParVar(
    'ENGINE_PAR_TR_SMOOTH')
ENGINE_PAR_SCOMP_THRESHOLD = bEngineParVar(
    'ENGINE_PAR_SCOMP_THRESHOLD')
ENGINE_PAR_SCOMP_RATIO = bEngineParVar(
    'ENGINE_PAR_SCOMP_RATIO')
ENGINE_PAR_SCOMP_ATTACK = bEngineParVar(
    'ENGINE_PAR_SCOMP_ATTACK')
ENGINE_PAR_SCOMP_RELEASE = bEngineParVar(
    'ENGINE_PAR_SCOMP_RELEASE')
ENGINE_PAR_SCOMP_MAKEUP = bEngineParVar(
    'ENGINE_PAR_SCOMP_MAKEUP')
ENGINE_PAR_SCOMP_MIX = bEngineParVar(
    'ENGINE_PAR_SCOMP_MIX')
ENGINE_PAR_JMP_PREAMP = bEngineParVar(
    'ENGINE_PAR_JMP_PREAMP')
ENGINE_PAR_JMP_BASS = bEngineParVar(
    'ENGINE_PAR_JMP_BASS')
ENGINE_PAR_JMP_MID = bEngineParVar(
    'ENGINE_PAR_JMP_MID')
ENGINE_PAR_JMP_TREBLE = bEngineParVar(
    'ENGINE_PAR_JMP_TREBLE')
ENGINE_PAR_JMP_MASTER = bEngineParVar(
    'ENGINE_PAR_JMP_MASTER')
ENGINE_PAR_JMP_PRESENCE = bEngineParVar(
    'ENGINE_PAR_JMP_PRESENCE')
ENGINE_PAR_JMP_HIGAIN = bEngineParVar(
    'ENGINE_PAR_JMP_HIGAIN')
ENGINE_PAR_JMP_MONO = bEngineParVar(
    'ENGINE_PAR_JMP_MONO')
ENGINE_PAR_FCOMP_INPUT = bEngineParVar(
    'ENGINE_PAR_FCOMP_INPUT')
ENGINE_PAR_FCOMP_RATIO = bEngineParVar(
    'ENGINE_PAR_FCOMP_RATIO')
ENGINE_PAR_FCOMP_ATTACK = bEngineParVar(
    'ENGINE_PAR_FCOMP_ATTACK')
ENGINE_PAR_FCOMP_RELEASE = bEngineParVar(
    'ENGINE_PAR_FCOMP_RELEASE')
ENGINE_PAR_FCOMP_MAKEUP = bEngineParVar(
    'ENGINE_PAR_FCOMP_MAKEUP')
ENGINE_PAR_FCOMP_MIX = bEngineParVar(
    'ENGINE_PAR_FCOMP_MIX')
ENGINE_PAR_FCOMP_HQ_MODE = bEngineParVar(
    'ENGINE_PAR_FCOMP_HQ_MODE')
ENGINE_PAR_FCOMP_LINK = bEngineParVar(
    'ENGINE_PAR_FCOMP_LINK')
ENGINE_PAR_AC_NORMALVOLUME = bEngineParVar(
    'ENGINE_PAR_AC_NORMALVOLUME')
ENGINE_PAR_AC_BRILLIANTVOLUME = bEngineParVar(
    'ENGINE_PAR_AC_BRILLIANTVOLUME')
ENGINE_PAR_AC_BASS = bEngineParVar(
    'ENGINE_PAR_AC_BASS')
ENGINE_PAR_AC_TREBLE = bEngineParVar(
    'ENGINE_PAR_AC_TREBLE')
ENGINE_PAR_AC_TONECUT = bEngineParVar(
    'ENGINE_PAR_AC_TONECUT')
ENGINE_PAR_AC_TREMOLOSPEED = bEngineParVar(
    'ENGINE_PAR_AC_TREMOLOSPEED')
ENGINE_PAR_AC_TREMOLODEPTH = bEngineParVar(
    'ENGINE_PAR_AC_TREMOLODEPTH')
ENGINE_PAR_AC_MONO = bEngineParVar(
    'ENGINE_PAR_AC_MONO')
ENGINE_PAR_CT_VOLUME = bEngineParVar(
    'ENGINE_PAR_CT_VOLUME')
ENGINE_PAR_CT_DISTORTION = bEngineParVar(
    'ENGINE_PAR_CT_DISTORTION')
ENGINE_PAR_CT_FILTER = bEngineParVar(
    'ENGINE_PAR_CT_FILTER')
ENGINE_PAR_CT_BASS = bEngineParVar(
    'ENGINE_PAR_CT_BASS')
ENGINE_PAR_CT_BALLS = bEngineParVar(
    'ENGINE_PAR_CT_BALLS')
ENGINE_PAR_CT_TREBLE = bEngineParVar(
    'ENGINE_PAR_CT_TREBLE')
ENGINE_PAR_CT_TONE = bEngineParVar(
    'ENGINE_PAR_CT_TONE')
ENGINE_PAR_CT_MONO = bEngineParVar(
    'ENGINE_PAR_CT_MONO')
ENGINE_PAR_DS_VOLUME = bEngineParVar(
    'ENGINE_PAR_DS_VOLUME')
ENGINE_PAR_DS_TONE = bEngineParVar(
    'ENGINE_PAR_DS_TONE')
ENGINE_PAR_DS_DRIVE = bEngineParVar(
    'ENGINE_PAR_DS_DRIVE')
ENGINE_PAR_DS_BASS = bEngineParVar(
    'ENGINE_PAR_DS_BASS')
ENGINE_PAR_DS_MID = bEngineParVar(
    'ENGINE_PAR_DS_MID')
ENGINE_PAR_DS_TREBLE = bEngineParVar(
    'ENGINE_PAR_DS_TREBLE')
ENGINE_PAR_DS_MONO = bEngineParVar(
    'ENGINE_PAR_DS_MONO')
ENGINE_PAR_HS_PRENORMAL = bEngineParVar(
    'ENGINE_PAR_HS_PRENORMAL')
ENGINE_PAR_HS_PREOVERDRIVE = bEngineParVar(
    'ENGINE_PAR_HS_PREOVERDRIVE')
ENGINE_PAR_HS_BASS = bEngineParVar(
    'ENGINE_PAR_HS_BASS')
ENGINE_PAR_HS_MID = bEngineParVar(
    'ENGINE_PAR_HS_MID')
ENGINE_PAR_HS_TREBLE = bEngineParVar(
    'ENGINE_PAR_HS_TREBLE')
ENGINE_PAR_HS_MASTER = bEngineParVar(
    'ENGINE_PAR_HS_MASTER')
ENGINE_PAR_HS_PRESENCE = bEngineParVar(
    'ENGINE_PAR_HS_PRESENCE')
ENGINE_PAR_HS_DEPTH = bEngineParVar(
    'ENGINE_PAR_HS_DEPTH')
ENGINE_PAR_HS_OVERDRIVE = bEngineParVar(
    'ENGINE_PAR_HS_OVERDRIVE')
ENGINE_PAR_HS_MONO = bEngineParVar(
    'ENGINE_PAR_HS_MONO')
ENGINE_PAR_V5_PREGAINRHYTHM = bEngineParVar(
    'ENGINE_PAR_V5_PREGAINRHYTHM')
ENGINE_PAR_V5_PREGAINLEAD = bEngineParVar(
    'ENGINE_PAR_V5_PREGAINLEAD')
ENGINE_PAR_V5_BASS = bEngineParVar(
    'ENGINE_PAR_V5_BASS')
ENGINE_PAR_V5_MID = bEngineParVar(
    'ENGINE_PAR_V5_MID')
ENGINE_PAR_V5_TREBLE = bEngineParVar(
    'ENGINE_PAR_V5_TREBLE')
ENGINE_PAR_V5_POSTGAIN = bEngineParVar(
    'ENGINE_PAR_V5_POSTGAIN')
ENGINE_PAR_V5_RESONANCE = bEngineParVar(
    'ENGINE_PAR_V5_RESONANCE')
ENGINE_PAR_V5_PRESENCE = bEngineParVar(
    'ENGINE_PAR_V5_PRESENCE')
ENGINE_PAR_V5_LEADCHANNEL = bEngineParVar(
    'ENGINE_PAR_V5_LEADCHANNEL')
ENGINE_PAR_V5_HIGAIN = bEngineParVar(
    'ENGINE_PAR_V5_HIGAIN')
ENGINE_PAR_V5_BRIGHT = bEngineParVar(
    'ENGINE_PAR_V5_BRIGHT')
ENGINE_PAR_V5_CRUNCH = bEngineParVar(
    'ENGINE_PAR_V5_CRUNCH')
ENGINE_PAR_V5_MONO = bEngineParVar(
    'ENGINE_PAR_V5_MONO')
ENGINE_PAR_CUTOFF = bEngineParVar(
    'ENGINE_PAR_CUTOFF')
ENGINE_PAR_RESONANCE = bEngineParVar(
    'ENGINE_PAR_RESONANCE')
ENGINE_PAR_EFFECT_BYPASS = bEngineParVar(
    'ENGINE_PAR_EFFECT_BYPASS')
ENGINE_PAR_GAIN = bEngineParVar(
    'ENGINE_PAR_GAIN')
ENGINE_PAR_FILTER_LADDER_HQ = bEngineParVar(
    'ENGINE_PAR_FILTER_LADDER_HQ')
ENGINE_PAR_BANDWIDTH = bEngineParVar(
    'ENGINE_PAR_BANDWIDTH')
ENGINE_PAR_FILTER_SHIFTB = bEngineParVar(
    'ENGINE_PAR_FILTER_SHIFTB')
ENGINE_PAR_FILTER_SHIFTC = bEngineParVar(
    'ENGINE_PAR_FILTER_SHIFTC')
ENGINE_PAR_FILTER_RESB = bEngineParVar(
    'ENGINE_PAR_FILTER_RESB')
ENGINE_PAR_FILTER_RESC = bEngineParVar(
    'ENGINE_PAR_FILTER_RESC')
ENGINE_PAR_FILTER_TYPEA = bEngineParVar(
    'ENGINE_PAR_FILTER_TYPEA')
ENGINE_PAR_FILTER_TYPEB = bEngineParVar(
    'ENGINE_PAR_FILTER_TYPEB')
ENGINE_PAR_FILTER_TYPEC = bEngineParVar(
    'ENGINE_PAR_FILTER_TYPEC')
ENGINE_PAR_FILTER_BYPA = bEngineParVar(
    'ENGINE_PAR_FILTER_BYPA')
ENGINE_PAR_FILTER_BYPB = bEngineParVar(
    'ENGINE_PAR_FILTER_BYPB')
ENGINE_PAR_FILTER_BYPC = bEngineParVar(
    'ENGINE_PAR_FILTER_BYPC')
ENGINE_PAR_FILTER_GAIN = bEngineParVar(
    'ENGINE_PAR_FILTER_GAIN')
ENGINE_PAR_FORMANT_TALK = bEngineParVar(
    'ENGINE_PAR_FORMANT_TALK')
ENGINE_PAR_FORMANT_SHARP = bEngineParVar(
    'ENGINE_PAR_FORMANT_SHARP')
ENGINE_PAR_FORMANT_SIZE = bEngineParVar(
    'ENGINE_PAR_FORMANT_SIZE')
ENGINE_PAR_LP_CUTOFF = bEngineParVar(
    'ENGINE_PAR_LP_CUTOFF')
ENGINE_PAR_HP_CUTOFF = bEngineParVar(
    'ENGINE_PAR_HP_CUTOFF')
ENGINE_PAR_FREQ1 = bEngineParVar(
    'ENGINE_PAR_FREQ1')
ENGINE_PAR_BW1 = bEngineParVar(
    'ENGINE_PAR_BW1')
ENGINE_PAR_GAIN1 = bEngineParVar(
    'ENGINE_PAR_GAIN1')
ENGINE_PAR_FREQ2 = bEngineParVar(
    'ENGINE_PAR_FREQ2')
ENGINE_PAR_BW2 = bEngineParVar(
    'ENGINE_PAR_BW2')
ENGINE_PAR_GAIN2 = bEngineParVar(
    'ENGINE_PAR_GAIN2')
ENGINE_PAR_FREQ3 = bEngineParVar(
    'ENGINE_PAR_FREQ3')
ENGINE_PAR_BW3 = bEngineParVar(
    'ENGINE_PAR_BW3')
ENGINE_PAR_GAIN3 = bEngineParVar(
    'ENGINE_PAR_GAIN3')
ENGINE_PAR_SEQ_LF_GAIN = bEngineParVar(
    'ENGINE_PAR_SEQ_LF_GAIN')
ENGINE_PAR_SEQ_LF_FREQ = bEngineParVar(
    'ENGINE_PAR_SEQ_LF_FREQ')
ENGINE_PAR_SEQ_LF_BELL = bEngineParVar(
    'ENGINE_PAR_SEQ_LF_BELL')
ENGINE_PAR_SEQ_LMF_GAIN = bEngineParVar(
    'ENGINE_PAR_SEQ_LMF_GAIN')
ENGINE_PAR_SEQ_LMF_FREQ = bEngineParVar(
    'ENGINE_PAR_SEQ_LMF_FREQ')
ENGINE_PAR_SEQ_LMF_Q = bEngineParVar(
    'ENGINE_PAR_SEQ_LMF_Q')
ENGINE_PAR_SEQ_HMF_GAIN = bEngineParVar(
    'ENGINE_PAR_SEQ_HMF_GAIN')
ENGINE_PAR_SEQ_HMF_FREQ = bEngineParVar(
    'ENGINE_PAR_SEQ_HMF_FREQ')
ENGINE_PAR_SEQ_HMF_Q = bEngineParVar(
    'ENGINE_PAR_SEQ_HMF_Q')
ENGINE_PAR_SEQ_HF_GAIN = bEngineParVar(
    'ENGINE_PAR_SEQ_HF_GAIN')
ENGINE_PAR_SEQ_HF_FREQ = bEngineParVar(
    'ENGINE_PAR_SEQ_HF_FREQ')
ENGINE_PAR_SEQ_HF_BELL = bEngineParVar(
    'ENGINE_PAR_SEQ_HF_BELL')
ENGINE_PAR_SEND_EFFECT_BYPASS = bEngineParVar(
    'ENGINE_PAR_SEND_EFFECT_BYPASS')
ENGINE_PAR_SEND_EFFECT_DRY_LEVEL = bEngineParVar(
    'ENGINE_PAR_SEND_EFFECT_DRY_LEVEL')
ENGINE_PAR_SEND_EFFECT_OUTPUT_GAIN = bEngineParVar(
    'ENGINE_PAR_SEND_EFFECT_OUTPUT_GAIN')
ENGINE_PAR_PH_DEPTH = bEngineParVar(
    'ENGINE_PAR_PH_DEPTH')
ENGINE_PAR_PH_SPEED = bEngineParVar(
    'ENGINE_PAR_PH_SPEED')
ENGINE_PAR_PH_SPEED_UNIT = bEngineParVar(
    'ENGINE_PAR_PH_SPEED_UNIT')
ENGINE_PAR_PH_PHASE = bEngineParVar(
    'ENGINE_PAR_PH_PHASE')
ENGINE_PAR_PH_FEEDBACK = bEngineParVar(
    'ENGINE_PAR_PH_FEEDBACK')
ENGINE_PAR_FL_DEPTH = bEngineParVar(
    'ENGINE_PAR_FL_DEPTH')
ENGINE_PAR_FL_SPEED = bEngineParVar(
    'ENGINE_PAR_FL_SPEED')
ENGINE_PAR_FL_SPEED_UNIT = bEngineParVar(
    'ENGINE_PAR_FL_SPEED_UNIT')
ENGINE_PAR_FL_PHASE = bEngineParVar(
    'ENGINE_PAR_FL_PHASE')
ENGINE_PAR_FL_FEEDBACK = bEngineParVar(
    'ENGINE_PAR_FL_FEEDBACK')
ENGINE_PAR_FL_COLOR = bEngineParVar(
    'ENGINE_PAR_FL_COLOR')
ENGINE_PAR_CH_DEPTH = bEngineParVar(
    'ENGINE_PAR_CH_DEPTH')
ENGINE_PAR_CH_SPEED = bEngineParVar(
    'ENGINE_PAR_CH_SPEED')
ENGINE_PAR_CH_SPEED_UNIT = bEngineParVar(
    'ENGINE_PAR_CH_SPEED_UNIT')
ENGINE_PAR_CH_PHASE = bEngineParVar(
    'ENGINE_PAR_CH_PHASE')
ENGINE_PAR_RV_PREDELAY = bEngineParVar(
    'ENGINE_PAR_RV_PREDELAY')
ENGINE_PAR_RV_SIZE = bEngineParVar(
    'ENGINE_PAR_RV_SIZE')
ENGINE_PAR_RV_COLOUR = bEngineParVar(
    'ENGINE_PAR_RV_COLOUR')
ENGINE_PAR_RV_STEREO = bEngineParVar(
    'ENGINE_PAR_RV_STEREO')
ENGINE_PAR_RV_DAMPING = bEngineParVar(
    'ENGINE_PAR_RV_DAMPING')
ENGINE_PAR_DL_TIME = bEngineParVar(
    'ENGINE_PAR_DL_TIME')
ENGINE_PAR_DL_TIME_UNIT = bEngineParVar(
    'ENGINE_PAR_DL_TIME_UNIT')
ENGINE_PAR_DL_DAMPING = bEngineParVar(
    'ENGINE_PAR_DL_DAMPING')
ENGINE_PAR_DL_PAN = bEngineParVar(
    'ENGINE_PAR_DL_PAN')
ENGINE_PAR_DL_FEEDBACK = bEngineParVar(
    'ENGINE_PAR_DL_FEEDBACK')
ENGINE_PAR_IRC_PREDELAY = bEngineParVar(
    'ENGINE_PAR_IRC_PREDELAY')
ENGINE_PAR_IRC_LENGTH_RATIO_ER = bEngineParVar(
    'ENGINE_PAR_IRC_LENGTH_RATIO_ER')
ENGINE_PAR_IRC_FREQ_LOWPASS_ER = bEngineParVar(
    'ENGINE_PAR_IRC_FREQ_LOWPASS_ER')
ENGINE_PAR_IRC_FREQ_HIGHPASS_ER = bEngineParVar(
    'ENGINE_PAR_IRC_FREQ_HIGHPASS_ER')
ENGINE_PAR_IRC_LENGTH_RATIO_LR = bEngineParVar(
    'ENGINE_PAR_IRC_LENGTH_RATIO_LR')
ENGINE_PAR_IRC_FREQ_LOWPASS_LR = bEngineParVar(
    'ENGINE_PAR_IRC_FREQ_LOWPASS_LR')
ENGINE_PAR_IRC_FREQ_HIGHPASS_LR = bEngineParVar(
    'ENGINE_PAR_IRC_FREQ_HIGHPASS_LR')
ENGINE_PAR_GN_GAIN = bEngineParVar(
    'ENGINE_PAR_GN_GAIN')
ENGINE_PAR_MOD_TARGET_INTENSITY = bEngineParVar(
    'ENGINE_PAR_MOD_TARGET_INTENSITY')
MOD_TARGET_INVERT_SOURCE = bEngineParVar(
    'MOD_TARGET_INVERT_SOURCE')
ENGINE_PAR_INTMOD_BYPASS = bEngineParVar(
    'ENGINE_PAR_INTMOD_BYPASS')
ENGINE_PAR_ATK_CURVE = bEngineParVar(
    'ENGINE_PAR_ATK_CURVE')
ENGINE_PAR_ATTACK = bEngineParVar(
    'ENGINE_PAR_ATTACK')
ENGINE_PAR_ATTACK_UNIT = bEngineParVar(
    'ENGINE_PAR_ATTACK_UNIT')
ENGINE_PAR_HOLD = bEngineParVar(
    'ENGINE_PAR_HOLD')
ENGINE_PAR_HOLD_UNIT = bEngineParVar(
    'ENGINE_PAR_HOLD_UNIT')
ENGINE_PAR_DECAY = bEngineParVar(
    'ENGINE_PAR_DECAY')
ENGINE_PAR_DECAY_UNIT = bEngineParVar(
    'ENGINE_PAR_DECAY_UNIT')
ENGINE_PAR_SUSTAIN = bEngineParVar(
    'ENGINE_PAR_SUSTAIN')
ENGINE_PAR_RELEASE = bEngineParVar(
    'ENGINE_PAR_RELEASE')
ENGINE_PAR_RELEASE_UNIT = bEngineParVar(
    'ENGINE_PAR_RELEASE_UNIT')
ENGINE_PAR_DECAY1 = bEngineParVar(
    'ENGINE_PAR_DECAY1')
ENGINE_PAR_DECAY1_UNIT = bEngineParVar(
    'ENGINE_PAR_DECAY1_UNIT')
ENGINE_PAR_BREAK = bEngineParVar(
    'ENGINE_PAR_BREAK')
ENGINE_PAR_DECAY2 = bEngineParVar(
    'ENGINE_PAR_DECAY2')
ENGINE_PAR_DECAY2_UNIT = bEngineParVar(
    'ENGINE_PAR_DECAY2_UNIT')
ENGINE_PAR_INTMOD_FREQUENCY = bEngineParVar(
    'ENGINE_PAR_INTMOD_FREQUENCY')
ENGINE_PAR_INTMOD_FREQUENCY_UNIT = bEngineParVar(
    'ENGINE_PAR_INTMOD_FREQUENCY_UNIT')
ENGINE_PAR_LFO_DELAY = bEngineParVar(
    'ENGINE_PAR_LFO_DELAY')
ENGINE_PAR_LFO_DELAY_UNIT = bEngineParVar(
    'ENGINE_PAR_LFO_DELAY_UNIT')
ENGINE_PAR_INTMOD_PULSEWIDTH = bEngineParVar(
    'ENGINE_PAR_INTMOD_PULSEWIDTH')
ENGINE_PAR_LFO_SINE = bEngineParVar(
    'ENGINE_PAR_LFO_SINE')
ENGINE_PAR_LFO_RECT = bEngineParVar(
    'ENGINE_PAR_LFO_RECT')
ENGINE_PAR_LFO_TRI = bEngineParVar(
    'ENGINE_PAR_LFO_TRI')
ENGINE_PAR_LFO_SAW = bEngineParVar(
    'ENGINE_PAR_LFO_SAW')
ENGINE_PAR_LFO_RAND = bEngineParVar(
    'ENGINE_PAR_LFO_RAND')
ENGINE_PAR_GLIDE_COEF = bEngineParVar(
    'ENGINE_PAR_GLIDE_COEF')
ENGINE_PAR_GLIDE_COEF_UNIT = bEngineParVar(
    'ENGINE_PAR_GLIDE_COEF_UNIT')
ENGINE_PAR_EFFECT_TYPE = bEngineParVar(
    'ENGINE_PAR_EFFECT_TYPE')
ENGINE_PAR_SEND_EFFECT_TYPE = bEngineParVar(
    'ENGINE_PAR_SEND_EFFECT_TYPE')


class bEngineParConst(bEngineParVar):
    pass


class bEngParEffType(bEngineParConst):
    pass


EFFECT_TYPE_FILTER = bEngParEffType('EFFECT_TYPE_FILTER')
EFFECT_TYPE_COMPRESSOR = bEngParEffType('EFFECT_TYPE_COMPRESSOR')
EFFECT_TYPE_LIMITER = bEngParEffType('EFFECT_TYPE_LIMITER')
EFFECT_TYPE_INVERTER = bEngParEffType('EFFECT_TYPE_INVERTER')
EFFECT_TYPE_SURROUND_PANNER = bEngParEffType(
    'EFFECT_TYPE_SURROUND_PANNER')
EFFECT_TYPE_SHAPER = bEngParEffType('EFFECT_TYPE_SHAPER')
EFFECT_TYPE_LOFI = bEngParEffType('EFFECT_TYPE_LOFI')
EFFECT_TYPE_STEREO = bEngParEffType('EFFECT_TYPE_STEREO')
EFFECT_TYPE_DISTORTION = bEngParEffType('EFFECT_TYPE_DISTORTION')
EFFECT_TYPE_SEND_LEVELS = bEngParEffType('EFFECT_TYPE_SEND_LEVELS')
EFFECT_TYPE_PHASER = bEngParEffType('EFFECT_TYPE_PHASER')
EFFECT_TYPE_CHORUS = bEngParEffType('EFFECT_TYPE_CHORUS')
EFFECT_TYPE_FLANGER = bEngParEffType('EFFECT_TYPE_FLANGER')
EFFECT_TYPE_REVERB = bEngParEffType('EFFECT_TYPE_REVERB')
EFFECT_TYPE_DELAY = bEngParEffType('EFFECT_TYPE_DELAY')
EFFECT_TYPE_IRC = bEngParEffType('EFFECT_TYPE_IRC')
EFFECT_TYPE_GAINER = bEngParEffType('EFFECT_TYPE_GAINER')
EFFECT_TYPE_SKREAMER = bEngParEffType('EFFECT_TYPE_SKREAMER')
EFFECT_TYPE_ROTATOR = bEngParEffType('EFFECT_TYPE_ROTATOR')
EFFECT_TYPE_TWANG = bEngParEffType('EFFECT_TYPE_TWANG')
EFFECT_TYPE_CABINET = bEngParEffType('EFFECT_TYPE_CABINET')
EFFECT_TYPE_AET_FILTER = bEngParEffType('EFFECT_TYPE_AET_FILTER')
EFFECT_TYPE_TRANS_MASTER = bEngParEffType('EFFECT_TYPE_TRANS_MASTER')
EFFECT_TYPE_BUS_COMP = bEngParEffType('EFFECT_TYPE_BUS_COMP')
EFFECT_TYPE_TAPE_SAT = bEngParEffType('EFFECT_TYPE_TAPE_SAT')
EFFECT_TYPE_SOLID_GEQ = bEngParEffType('EFFECT_TYPE_SOLID_GEQ')
EFFECT_TYPE_JUMP = bEngParEffType('EFFECT_TYPE_JUMP')
EFFECT_TYPE_FB_COMP = bEngParEffType('EFFECT_TYPE_FB_COMP')
EFFECT_TYPE_ACBOX = bEngParEffType('EFFECT_TYPE_ACBOX')
EFFECT_TYPE_CAT = bEngParEffType('EFFECT_TYPE_CAT')
EFFECT_TYPE_DSTORTION = bEngParEffType('EFFECT_TYPE_DSTORTION')
EFFECT_TYPE_HOTSOLO = bEngParEffType('EFFECT_TYPE_HOTSOLO')
EFFECT_TYPE_VAN51 = bEngParEffType('EFFECT_TYPE_VAN51')
EFFECT_TYPE_NONE = bEngParEffType('EFFECT_TYPE_NONE')


EFFECT_TYPE_PHASER = bEngParEffType('EFFECT_TYPE_PHASER')
EFFECT_TYPE_CHORUS = bEngParEffType('EFFECT_TYPE_CHORUS')
EFFECT_TYPE_FLANGER = bEngParEffType('EFFECT_TYPE_FLANGER')
EFFECT_TYPE_REVERB = bEngParEffType('EFFECT_TYPE_REVERB')
EFFECT_TYPE_DELAY = bEngParEffType('EFFECT_TYPE_DELAY')
EFFECT_TYPE_IRC = bEngParEffType('EFFECT_TYPE_IRC')
EFFECT_TYPE_GAINER = bEngParEffType('EFFECT_TYPE_GAINER')


ENGINE_PAR_EFFECT_SUBTYPE = bEngineParVar(
    'ENGINE_PAR_EFFECT_SUBTYPE')


class bEngParEffSubType(bEngineParConst):
    pass


FILTER_TYPE_LP1POLE = bEngParEffSubType('FILTER_TYPE_LP1POLE')
FILTER_TYPE_HP1POLE = bEngParEffSubType('FILTER_TYPE_HP1POLE')
FILTER_TYPE_BP2POLE = bEngParEffSubType('FILTER_TYPE_BP2POLE')
FILTER_TYPE_LP2POLE = bEngParEffSubType('FILTER_TYPE_LP2POLE')
FILTER_TYPE_HP2POLE = bEngParEffSubType('FILTER_TYPE_HP2POLE')
FILTER_TYPE_LP4POLE = bEngParEffSubType('FILTER_TYPE_LP4POLE')
FILTER_TYPE_HP4POLE = bEngParEffSubType('FILTER_TYPE_HP4POLE')
FILTER_TYPE_BP4POLE = bEngParEffSubType('FILTER_TYPE_BP4POLE')
FILTER_TYPE_BR4POLE = bEngParEffSubType('FILTER_TYPE_BR4POLE')
FILTER_TYPE_LP6POLE = bEngParEffSubType('FILTER_TYPE_LP6POLE')
FILTER_TYPE_PHASER = bEngParEffSubType('FILTER_TYPE_PHASER')
FILTER_TYPE_VOWELA = bEngParEffSubType('FILTER_TYPE_VOWELA')
FILTER_TYPE_VOWELB = bEngParEffSubType('FILTER_TYPE_VOWELB')
FILTER_TYPE_PRO52 = bEngParEffSubType('FILTER_TYPE_PRO52')
FILTER_TYPE_LADDER = bEngParEffSubType('FILTER_TYPE_LADDER')
FILTER_TYPE_VERSATILE = bEngParEffSubType('FILTER_TYPE_VERSATILE')
FILTER_TYPE_EQ1BAND = bEngParEffSubType('FILTER_TYPE_EQ1BAND')
FILTER_TYPE_EQ2BAND = bEngParEffSubType('FILTER_TYPE_EQ2BAND')
FILTER_TYPE_EQ3BAND = bEngParEffSubType('FILTER_TYPE_EQ3BAND')
FILTER_TYPE_DAFT_LP = bEngParEffSubType('FILTER_TYPE_DAFT_LP')
FILTER_TYPE_SV_LP1 = bEngParEffSubType('FILTER_TYPE_SV_LP1')
FILTER_TYPE_SV_LP2 = bEngParEffSubType('FILTER_TYPE_SV_LP2')
FILTER_TYPE_SV_LP4 = bEngParEffSubType('FILTER_TYPE_SV_LP4')
FILTER_TYPE_LDR_LP1 = bEngParEffSubType('FILTER_TYPE_LDR_LP1')
FILTER_TYPE_LDR_LP2 = bEngParEffSubType('FILTER_TYPE_LDR_LP2')
FILTER_TYPE_LDR_LP3 = bEngParEffSubType('FILTER_TYPE_LDR_LP3')
FILTER_TYPE_LDR_LP4 = bEngParEffSubType('FILTER_TYPE_LDR_LP4')
FILTER_TYPE_AR_LP2 = bEngParEffSubType('FILTER_TYPE_AR_LP2')
FILTER_TYPE_AR_LP4 = bEngParEffSubType('FILTER_TYPE_AR_LP4')
FILTER_TYPE_AR_LP24 = bEngParEffSubType('FILTER_TYPE_AR_LP24')
FILTER_TYPE_SV_HP1 = bEngParEffSubType('FILTER_TYPE_SV_HP1')
FILTER_TYPE_SV_HP2 = bEngParEffSubType('FILTER_TYPE_SV_HP2')
FILTER_TYPE_SV_HP4 = bEngParEffSubType('FILTER_TYPE_SV_HP4')
FILTER_TYPE_LDR_HP1 = bEngParEffSubType('FILTER_TYPE_LDR_HP1')
FILTER_TYPE_LDR_HP2 = bEngParEffSubType('FILTER_TYPE_LDR_HP2')
FILTER_TYPE_LDR_HP3 = bEngParEffSubType('FILTER_TYPE_LDR_HP3')
FILTER_TYPE_LDR_HP4 = bEngParEffSubType('FILTER_TYPE_LDR_HP4')
FILTER_TYPE_AR_HP2 = bEngParEffSubType('FILTER_TYPE_AR_HP2')
FILTER_TYPE_AR_HP4 = bEngParEffSubType('FILTER_TYPE_AR_HP4')
FILTER_TYPE_AR_HP24 = bEngParEffSubType('FILTER_TYPE_AR_HP24')
FILTER_TYPE_DAFT_HP = bEngParEffSubType('FILTER_TYPE_DAFT_HP')
FILTER_TYPE_SV_BP2 = bEngParEffSubType('FILTER_TYPE_SV_BP2')
FILTER_TYPE_SV_BP4 = bEngParEffSubType('FILTER_TYPE_SV_BP4')
FILTER_TYPE_LDR_BP2 = bEngParEffSubType('FILTER_TYPE_LDR_BP2')
FILTER_TYPE_LDR_BP4 = bEngParEffSubType('FILTER_TYPE_LDR_BP4')
FILTER_TYPE_AR_BP2 = bEngParEffSubType('FILTER_TYPE_AR_BP2')
FILTER_TYPE_AR_BP4 = bEngParEffSubType('FILTER_TYPE_AR_BP4')
FILTER_TYPE_AR_BP24 = bEngParEffSubType('FILTER_TYPE_AR_BP24')
FILTER_TYPE_SV_NOTCH4 = bEngParEffSubType('FILTER_TYPE_SV_NOTCH4')
FILTER_TYPE_LDR_PEAK = bEngParEffSubType('FILTER_TYPE_LDR_PEAK')
FILTER_TYPE_LDR_NOTCH = bEngParEffSubType('FILTER_TYPE_LDR_NOTCH')
FILTER_TYPE_SV_PAR_LPHP = bEngParEffSubType('FILTER_TYPE_SV_PAR_LPHP')
FILTER_TYPE_SV_PAR_BPBP = bEngParEffSubType('FILTER_TYPE_SV_PAR_BPBP')
FILTER_TYPE_SV_SER_LPHP = bEngParEffSubType('FILTER_TYPE_SV_SER_LPHP')
FILTER_TYPE_FORMANT_1 = bEngParEffSubType('FILTER_TYPE_FORMANT_1')
FILTER_TYPE_FORMANT_2 = bEngParEffSubType('FILTER_TYPE_FORMANT_2')
FILTER_TYPE_SIMPLE_LPHP = bEngParEffSubType('FILTER_TYPE_SIMPLE_LPHP')

ENGINE_PAR_INTMOD_TYPE = bEngineParVar('ENGINE_PAR_INTMOD_TYPE')


class bEngParIntmodType(bEngineParConst):
    pass


INTMOD_TYPE_NONE = bEngParIntmodType('INTMOD_TYPE_NONE')
INTMOD_TYPE_LFO = bEngParIntmodType('INTMOD_TYPE_LFO')
INTMOD_TYPE_ENVELOPE = bEngParIntmodType('INTMOD_TYPE_ENVELOPE')
INTMOD_TYPE_STEPMOD = bEngParIntmodType('INTMOD_TYPE_STEPMOD')
INTMOD_TYPE_ENV_FOLLOW = bEngParIntmodType('INTMOD_TYPE_ENV_FOLLOW')
INTMOD_TYPE_GLIDE = bEngParIntmodType('INTMOD_TYPE_GLIDE')

ENGINE_PAR_INTMOD_SUBTYPE = bEngineParVar('ENGINE_PAR_INTMOD_SUBTYPE')


class bEngParIntmodSubType(bEngineParConst):
    pass


ENV_TYPE_AHDSR = bEngParIntmodSubType('ENV_TYPE_AHDSR')
ENV_TYPE_FLEX = bEngParIntmodSubType('ENV_TYPE_FLEX')
ENV_TYPE_DBD = bEngParIntmodSubType('ENV_TYPE_DBD')
LFO_TYPE_RECTANGLE = bEngParIntmodSubType('LFO_TYPE_RECTANGLE')
LFO_TYPE_TRIANGLE = bEngParIntmodSubType('LFO_TYPE_TRIANGLE')
LFO_TYPE_SAWTOOTH = bEngParIntmodSubType('LFO_TYPE_SAWTOOTH')
LFO_TYPE_RANDO = bEngParIntmodSubType('LFO_TYPE_RANDO')
LFO_TYPE_MULTI = bEngParIntmodSubType('LFO_TYPE_MULTI')

ENGINE_PAR_DISTORTION_TYPE = bEngineParVar('ENGINE_PAR_DISTORTION_TYPE')


class bEngParDistType(bEngineParConst):
    pass


NI_DISTORTION_TYPE_TUBE = bEngParDistType('NI_DISTORTION_TYPE_TUBE')
NI_DISTORTION_TYPE_TRANS = bEngParDistType('NI_DISTORTION_TYPE_TRANS')

ENGINE_PAR_SHAPE_TYPE = bEngineParVar('ENGINE_PAR_SHAPE_TYPE')


class bEngParShapeType(bEngineParConst):
    pass


NI_SHAPE_TYPE_CLASSIC = bEngParShapeType('NI_SHAPE_TYPE_CLASSIC')
NI_SHAPE_TYPE_ENHANCED = bEngParShapeType('NI_SHAPE_TYPE_ENHANCED')
NI_SHAPE_TYPE_DRUMS = bEngParShapeType('NI_SHAPE_TYPE_DRUMS')


ENGINE_PAR_START_CRITERIA_MODE = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_MODE')
ENGINE_PAR_START_CRITERIA_KEY_MIN = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_KEY_MIN')
ENGINE_PAR_START_CRITERIA_KEY_MAX = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_KEY_MAX')
ENGINE_PAR_START_CRITERIA_CONTROLLER = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_CONTROLLER')
ENGINE_PAR_START_CRITERIA_CC_MIN = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_CC_MIN')
ENGINE_PAR_START_CRITERIA_CC_MAX = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_CC_MAX')
ENGINE_PAR_START_CRITERIA_CYCLE_CLASS = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_CYCLE_CLASS')
ENGINE_PAR_START_CRITERIA_ZONE_IDX = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_ZONE_IDX')
ENGINE_PAR_START_CRITERIA_SLICE_IDX = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_SLICE_IDX')
ENGINE_PAR_START_CRITERIA_SEQ_ONLY = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_SEQ_ONLY')
ENGINE_PAR_START_CRITERIA_NEXT_CRIT = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_NEXT_CRIT')
ENGINE_PAR_START_CRITERIA_MODE = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_MODE')
ENGINE_PAR_START_CRITERIA_NEXT_CRIT = bEngineParVar(
    'ENGINE_PAR_START_CRITERIA_NEXT_CRIT')


class bEngGroupStartCritMode(bEngineParVar):
    pass


START_CRITERIA_NONE = bEngGroupStartCritMode(
    'START_CRITERIA_NONE')
START_CRITERIA_ON_KEY = bEngGroupStartCritMode(
    'START_CRITERIA_ON_KEY')
START_CRITERIA_ON_CONTROLLER = bEngGroupStartCritMode(
    'START_CRITERIA_ON_CONTROLLER')
START_CRITERIA_CYCLE_ROUND_ROBIN = bEngGroupStartCritMode(
    'START_CRITERIA_CYCLE_ROUND_ROBIN')
START_CRITERIA_CYCLE_RANDOM = bEngGroupStartCritMode(
    'START_CRITERIA_CYCLE_RANDOM')
START_CRITERIA_SLICE_TRIGGER = bEngGroupStartCritMode(
    'START_CRITERIA_SLICE_TRIGGER')


class bEngGroupStartCritNext(bEngineParVar):
    pass


START_CRITERIA_AND_NEXT = bEngineParVar('START_CRITERIA_AND_NEXT')
START_CRITERIA_AND_NOT_NEXT = bEngineParVar('START_CRITERIA_AND_NOT_NEXT')
START_CRITERIA_OR_NEXT = bEngineParVar('START_CRITERIA_OR_NEXT')


class FindMod(BuiltInFuncInt):

    def __init__(self):
        super().__init__('find_mod',
                         args=OrderedDict(group_idx=int, mod_name=str),
                         def_ret=1)

    def __call__(self, group_idx: int, mod_name: str):
        '''returns the slot index of an internal modulator or external
        modulation slot
        <group-index>
        the index of the group
        <mod-name>
        the name of the modulator or modulation slot
        Each modulator or modulation slot has a predefined name, based
        on the modulation source and target.
        The name can be changed with the script editor's edit area open
        and right-clicking on the modulator or modulation slot.'''
        return super().__call__(group_idx, mod_name)


find_mod = FindMod().__call__


class FindTarget(BuiltInFuncInt):

    def __init__(self):
        super().__init__('find_target',
                         args=OrderedDict(group_idx=int, mod_idx=int,
                                          target_name=str),
                         def_ret=1)

    def __call__(self, group_idx: int, mod_idx: int,
                 target_name: str):
        '''returns the slot index of a modulation slot of an
        internal modulator
        <group-index>
        the index of the group
        <mod-index>
        the slot index of the internal modulator. Can be retrieved with
        find_mod(<group-idx>,<mod-name>)
        <target-name>
        the name of the modulation slot
        Each modulation slot has a predefined name, based on the
        modulation source and target.
        The name can be changed with the script editor's edit area open
        and right-clicking on the modulation slot.'''
        return super().__call__(group_idx, mod_idx, target_name)


find_target = FindTarget().__call__


class EngineUnit(KSP):

    def __init__(self):
        self.parameters = dict()

    def set_par(self, par, val):
        self.parameters[par.id] = val

    def get_par(self, par):
        if par.id not in self.parameters:
            return None
        return self.parameters[par.id]


class EnginePars(metaclass=SingletonMeta):

    def __init__(self):
        self.pars = dict()

    def set_par(self, par, group, slot, generic, val):
        key = self._get_key(group, slot, generic)
        if key not in self.pars:
            self.pars[key] = EngineUnit()
        self.pars[key].set_par(par, val)

    def get_par(self, par, group, slot, generic):
        key = self._get_key(group, slot, generic)
        if key not in self.pars:
            self.pars[key] = EngineUnit()
        return self.pars[key].get_par(par)

    def _get_key(self, group, slot, generic):
        group = get_runtime_val(group)
        slot = get_runtime_val(slot)
        generic = get_runtime_val(generic)
        # if group > -1:
        #     if generic > -1:
        #         raise AttributeError(
        #             'with group index generic has to be -1')

        key = f'{group}{slot}{generic}'
        return key


class GetEnginePar(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_engine_par',
                         args=OrderedDict(parameter=bEngineParVar,
                                          group_idx=int,
                                          slot=int,
                                          generic=int))

    def __call__(self, parameter: bEngineParVar, group_idx: int,
                 slot: int, generic: int):
        '''returns the slot index of a modulation slot of an
        internal modulator
        <group-index>
        the index of the group
        <mod-index>
        the slot index of the internal modulator. Can be retrieved with
        find_mod(<group-idx>,<mod-name>)
        <target-name>
        the name of the modulation slot
        Each modulation slot has a predefined name, based on the
        modulation source and target.
        The name can be changed with the script editor's edit area open
        and right-clicking on the modulation slot.'''
        return super().__call__(parameter, group_idx, slot, generic)

    def calculate(self, parameter, group_idx, slot, generic):
        ret = EnginePars().get_par(parameter, group_idx, slot, generic)
        if ret is None:
            return 1
        return ret


get_engine_par = GetEnginePar().__call__


class GetEngineParDisp(BuiltInFuncStr):

    def __init__(self):
        super().__init__('get_engine_par_disp',
                         args=OrderedDict(parameter=bEngineParVar,
                                          group_idx=int,
                                          slot=int,
                                          generic=int))

    def __call__(self, parameter: bEngineParVar, group_idx: int,
                 slot: int, generic: int):
        '''returns the displayed string of a specific engine parameter
        <group-index>
        the index of the group
        <mod-index>
        the slot index of the internal modulator. Can be retrieved with
        find_mod(<group-idx>,<mod-name>)
        <target-name>
        the name of the modulation slot
        Each modulation slot has a predefined name, based on the
        modulation source and target.
        The name can be changed with the script editor's edit area open
        and right-clicking on the modulation slot.'''
        return super().__call__(parameter, group_idx, slot, generic)

    def calculate(self, parameter, group_idx, slot, generic):
        ret = EnginePars().get_par(parameter, group_idx, slot, generic)
        if ret is None:
            return 'display'
        return f'{get_runtime_val(ret)}'


get_engine_par_disp = GetEngineParDisp().__call__


class GetVoiceLimit(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_voice_limit',
                         args=OrderedDict(voice_type=bTmProVar),
                         def_ret=4)

    def __call__(self, voice_type: bTmProVar):
        '''retunrs the voice limit for the Time Machine Pro mode of the
        source module
        <voice-type>
        the voice type, can be one one of the following:
        $NI_VL_TMPRO_STANDARD {Standard Mode}
        $NI_VL_TMRPO_HQ {High Quality Mode}'''
        return super().__call__(voice_type)


get_voice_limit = GetVoiceLimit().__call__


class SetVoiceLimit(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_voice_limit',
                         args=OrderedDict(voice_type=bTmProVar,
                                          value=int),
                         def_ret=kNone())

    def __call__(self, voice_type: bTmProVar, value: int):
        '''retunrs the voice limit for the Time Machine Pro mode of the
        source module
        <voice-type>
        the voice type, can be one one of the following:
        $NI_VL_TMPRO_STANDARD {Standard Mode}
        $NI_VL_TMRPO_HQ {High Quality Mode}'''
        val_rt = get_runtime_val(value)
        voice_type.set_value(val_rt)
        return super().__call__(voice_type, value)


set_voice_limit = SetVoiceLimit().__call__


class OutputChannelName(BuiltInFuncStr):

    def __init__(self):
        super().__init__('output_channel_name',
                         args=OrderedDict(out_number=int),
                         def_ret='out_cahnnel')

    def __call__(self, out_number: int):
        '''returns the channel name for the specified output
        <output-number>
        the number of the output channel (zero based, i.e.
        the first output is 0)'''
        return super().__call__(out_number)


output_channel_name = OutputChannelName().__call__


class SetEnginePar(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_engine_par',
                         args=OrderedDict(parameter=bEngineParVar,
                                          value=int,
                                          group_idx=int,
                                          slot=int,
                                          generic=int),
                         def_ret=kNone())

    def __call__(self, parameter: bEngineParVar, value: int,
                 group_idx: int, slot: int, generic: int):
        '''returns the slot index of a modulation slot of an
        internal modulator
        <group-index>
        the index of the group
        <mod-index>
        the slot index of the internal modulator. Can be retrieved with
        find_mod(<group-idx>,<mod-name>)
        <target-name>
        the name of the modulation slot
        Each modulation slot has a predefined name, based on the
        modulation source and target.
        The name can be changed with the script editor's edit area open
        and right-clicking on the modulation slot.'''
        EnginePars().set_par(parameter, group_idx, slot, generic, value)
        return super().__call__(parameter, value, group_idx,
                                slot, generic)


set_engine_par = SetEnginePar().__call__
