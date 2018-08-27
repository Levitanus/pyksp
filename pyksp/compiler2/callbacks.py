from functools import wraps
from inspect import signature

from k_built_ins import InitCallback as _InitCallback
from k_built_ins import AsyncCompleteCallback as _AsyncCompleteCallback
from k_built_ins import ListenerCallback as _ListenerCallback
from k_built_ins import PersistenceCallback as _PersistenceCallback
from k_built_ins import PgsCallback as _PgsCallback
from k_built_ins import PolyAtCallback as _PolyAtCallback
from k_built_ins import NoteCallback as _NoteCallback
from k_built_ins import ReleaseCallback as _ReleaseCallback
from k_built_ins import ControllerCallback as _ControllerCallback
from k_built_ins import RpnCallback as _RpnCallback
from k_built_ins import UiUpdateCallback as _UiUpdateCallback


def _cb_wrapper(cb, f, obj=None):
    cb.open()
    sig = signature(f)
    if not sig.parameters:
        out = f()
    else:
        print(sig.parameters)
        try:
            obj = sig.parameters['self']
            out = f(obj)
        except AttributeError as e:
            raise RuntimeError(
                'probably, used as decorator of class method. Invoke ' +
                'as function with method name as argument. ' +
                'Example: init(self.method)' +
                'or use as decorator with no arguments passed\n' +
                f'original exception: {e}')
    cb.close()
    return out


def init(f):
    '''adds body of decorated function to KSP init callback'''

    return wraps(_cb_wrapper(_InitCallback, f), f)


def async_comlete(f):
    '''adds body of decorated function to KSP async_comlete callback'''

    return wraps(_cb_wrapper(_AsyncCompleteCallback, f), f)


def listener(f):
    '''adds body of decorated function to KSP listener callback'''
    return wraps(_cb_wrapper(_ListenerCallback, f), f)


def persistence_changed(f):
    '''adds body of decorated function to KSP
    persistence_changed callback'''

    return wraps(_cb_wrapper(_PersistenceCallback, f), f)


def pgs_changed(f):
    '''adds body of decorated function to KSP
    pgs_changed callback'''

    return wraps(_cb_wrapper(_PgsCallback, f), f)


def poly_at(f):
    '''adds body of decorated function to KSP
    poly_at callback'''

    return wraps(_cb_wrapper(_PolyAtCallback, f), f)


def note(f):
    '''adds body of decorated function to KSP
    release callback'''

    return wraps(_cb_wrapper(_NoteCallback, f), f)


def release(f):
    '''adds body of decorated function to KSP
    release callback'''

    return wraps(_cb_wrapper(_ReleaseCallback, f), f)


def controller(f):
    '''adds body of decorated function to KSP
    release callback'''

    return wraps(_cb_wrapper(_ControllerCallback, f), f)


def rpn_nrpn(f):
    '''adds body of decorated function to KSP
    rpn/nrpn callback'''

    return wraps(_cb_wrapper(_RpnCallback, f), f)


def ui_update(f):
    '''adds body of decorated function to KSP
    ui_update callback'''

    return wraps(_cb_wrapper(_UiUpdateCallback, f), f)
