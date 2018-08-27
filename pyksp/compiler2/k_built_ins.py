from abc import abstractmethod
from functools import wraps

from abstract import KspObject
from abstract import Output
from abstract import KSP

from base_types import KspVar
from base_types import KspArray

from native_types import kInt
from native_types import kArrInt
from native_types import kStr
from native_types import kReal
from native_types import kArrReal
from native_types import kNone

from conditions_loops import For
from conditions_loops import If
from conditions_loops import check

from ui_system import kWidget

all_callbacks = object()


def _all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__()
         for s in _all_subclasses(c)])


class Callback(KSP):

    __callbacks = list()
    __current = None

    def __init__(self, header: str):
        Callback.__callbacks.append(self)
        self._header = header
        self.__lines = list()

    def open(self):
        Output().set(self.__lines)
        self.set_callback(self)

    def close(self):
        Output().release()
        self.set_callback(None)

    def generate_body(self):
        if not self.__lines:
            return []
        out = list()
        out.append(f'on {self._header}')
        out.extend(self.__lines)
        out.append(f'end on')
        return out

    @staticmethod
    def get_all_bodies():
        out = list()
        for cb in Callback.__callbacks:
            out.extend(cb.generate_body())
        return out

    @staticmethod
    def refresh():
        for cb in Callback.__callbacks:
            cb._refresh()
        KSP.set_callback(None)

    def _refresh(self):
        self.__lines.clear()


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

    def __init__(self):
        super().__init__('ui_control')
        self.__controls = dict()

    def open(self, control: KspVar):
        super().open()
        if control.name() in self.__controls.keys():
            raise RuntimeError(f'callback of {control.name()} has' +
                               ' been set yet')
        self.__controls[control.name()] = Control(control)
        Output().release()
        Output().set(self.__controls[control.name()].lines)

    def generate_body(self):
        if not self.__controls:
            return []
        out = list()
        for name, control in self.__controls.items():
            out.append(f'on {self._header}({name})')
            out.extend(control.lines)
            out.append(f'end on')
        return out


class FunctionCallbackCl(Callback):

    def __init__(self):
        super().__init__('function')
        self.__root = None
        self.__levels = 0

    def open(self):
        if self.callback() is None:
            self.__levels = 1
            return self.set_callback(self)
        if self.callback() is self:
            self.__levels += 1
            return
        self.__root = self.callback()
        self.__root.close()
        self.set_callback(self)

    def close(self):
        if self.callback() is self:
            self.__levels -= 1
            if self.__levels == 0:
                self.set_callback(None)
            return
        self.set_callback(None)
        self.__root.open()
        self.__root = None
        return

    def generate_body(self):
        return []


AsyncCompleteCallback = Callback('async_comlete')
ControllerCallback = Callback('controller')
InitCallback = Callback('init')
ListenerCallback = Callback('listener')
NoteCallback = Callback('note')
PersistenceCallback = Callback('persistence_changed')
PgsCallback = Callback('pgs_changed')
PolyAtCallback = Callback('poly_at')
ReleaseCallback = Callback('release')
RpnCallback = Callback('rpn/nrpn')
UiUpdateCallback = Callback('ui_update')
UiControlCallback = UiControlCallbackCl()
FunctionCallback = FunctionCallbackCl()


class BuiltInID(kInt):

    def __init__(self, name: str, obj: object):
        cls = type(self)
        if '_instances' not in cls.__dict__:
            setattr(cls, '_instances', list())
        if '_count' not in cls.__dict__:
            setattr(cls, '_count', int())

        cls._instances.append(self)
        self._obj = obj
        super().__init__(value=self._count,
                         name=name,
                         preserve=False,
                         is_local=True,
                         persist=False)
        cls._count += 1

    @classmethod
    def get_by_id(cls, idx):
        if hasattr(idx, '_get_runtime'):
            idx = idx._get_runtime()
        return cls._instances[idx]._obj

    @property
    def obj(self):
        return self._obj

    @staticmethod
    def refresh():
        cls = BuiltInID
        cls._instances = list()
        cls._count = int()
        subclasses = _all_subclasses(cls)
        for _class in subclasses:
            _class._instances = list()
            _class._count = int()


class BuiltIn(KspVar):

    def __init__(self, name: str, callbacks=all_callbacks,
                 ret_type: type=BuiltInID, ret_value: object=None):
        self.name = name
        ref_type, value = self._get_return_value(ret_type, ret_value)
        name = value.name()
        super().__init__(name,
                         value=None,
                         ref_type=ref_type,
                         name_prefix='',
                         name_postfix='',
                         preserve_name=False,
                         has_init=False,
                         is_local=True,
                         persist=False)
        self._value_holder = value
        self._callbacks = callbacks

    def _get_return_value(self, ret_type, ret_value):
        if ret_type is BuiltInID:
            if ret_value:
                raise TypeError(
                    'is not alllowed to use ret_value within BuiltInID')
            _id = BuiltInID(self.name, self)
            return _id.ref_type, _id
        if not ret_value:
            val = ret_type(name=self.name)
            return val.ref_type, val
        if issubclass(ret_type, KspArray):
            val = ret_type(name=self.name, sequence=ret_value,
                           is_local=True)
        else:
            val = ret_type(name=self.name, value=ret_value,
                           is_local=True)
        return val.ref_type, val

    def __rshift__(self, other):
        raise NotImplementedError('builtin object can not be assigned')

    def _generate_executable(self):
        raise NotImplementedError

    def _generate_init(self):
        raise NotImplementedError

    def _get_compiled(self):
        self._check_callback()
        return self._value_holder._get_compiled()

    def _get_runtime(self):
        self._check_callback()
        return self._value_holder._get_runtime()

    def _set_runtime(self, val):
        raise NotImplementedError

    def _check_callback(self):
        if self._callbacks is all_callbacks:
            return
        if self.in_init() and InitCallback in self._callbacks:
            return
        if KSP.callback() not in self._callbacks:
            raise RuntimeError(
                f'can be used only in {self._callbacks} callbacks')


class NativeControlPar(KSP):

    def __init__(self, fget, fset, arr_type, arr_name, control_par):
        self._getter = fget
        self._setter = fset
        self.arr_type = arr_type
        self.inits = dict()
        self.arr_name = arr_name
        self._control_par = control_par
        self._assigned = False

    @property
    def control_par(self):
        return self._control_par

    def none_to_dict(self, obj):
        self.inits[repr(obj)] = None

    def init_array(self):
        # print([val for key, val in self.inits.items()])
        seq = list()
        for key, val in self.inits.items():
            if val is None:
                seq.append(kNone())
                continue
            seq.append(val)
        return self.arr_type(seq, name=self.arr_name)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return self._getter(obj)

    def __set__(self, obj, val):
        self._assigned = True
        # print(f'set {val}')
        if self.inits[repr(obj)] is None:
            # print(f'self.inits[{repr(obj)}]')
            self.inits[repr(obj)] = val
        else:
            self._control_par.set(obj.id, val)
        self._setter(obj, val)

    def set_raw(self, obj, val):
        self._assigned = True
        self._setter(obj, val)

    @property
    def assigned(self):
        return self._assigned


class kNativeControl(kWidget, KspVar):

    _controls = list()
    _ids_count = 0
    _init_is_generated = False

    @staticmethod
    def refresh():
        kNativeControl._controls = list()
        kNativeControl._ids_count = 0
        kNativeControl._init_is_generated = False
        subclasses = _all_subclasses(kNativeControl)
        for cls in subclasses:
            if hasattr(cls, '_types_controls'):
                cls._types_controls = list()
            if hasattr(cls, '_ids'):
                cls._ids = kArrInt(name=f'_{cls.__name__}_ids')
        # NativeControlPar.refresh()

    def __init__(self, var, parent: object=None,
                 x: int=None, y: int=None,
                 width: int=None, height: int=None):
        self._var = var
        cls = self.__class__

        kNativeControl._controls.append(self)
        if not hasattr(cls, '_types_controls'):
            cls._types_controls = list()
        cls._types_controls.append(self)
        cls_name = cls.__name__
        if not hasattr(cls, '_ids'):
            cls._ids = kArrInt(name=f'_{cls_name}_ids')
        ids = cls._ids

        blocked = False
        if not Output().blocked:
            blocked = True
            Output().blocked = True
        ids.append(kNativeControl._ids_count)
        if blocked:
            Output().blocked = False
        self._id = ids[-1]
        # if 'x' not in cls.__dict__:
        KspVar.__init__(self, var.name(),
                        value=None,
                        ref_type=var.ref_type,
                        name_prefix='',
                        name_postfix='',
                        preserve_name=False,
                        has_init=True,
                        is_local=False,
                        persist=False)
        super().__init__(parent=parent,
                         x=x,
                         y=y,
                         width=width,
                         height=height)

        if cls.x == kNativeControl.x:
            cls.x = NativeControlPar(cls._get_x, cls._set_x,
                                     kArrInt, f'_{cls_name}_x',
                                     CONTROL_PAR_POS_X)
        cls.x.none_to_dict(self)
        if x:
            self.x = x
        if cls.y == kNativeControl.y:
            cls.y = NativeControlPar(cls._get_y, cls._set_y,
                                     kArrInt, f'_{cls_name}_y',
                                     CONTROL_PAR_POS_X)
        cls.y.none_to_dict(self)
        if y:
            self.y = y
        if cls.width == kNativeControl.width:
            cls.width = NativeControlPar(cls._get_width, cls._set_width,
                                         kArrInt, f'_{cls_name}_width',
                                         CONTROL_PAR_POS_X)
        cls.width.none_to_dict(self)
        if width:
            self.width = width
        if cls.height == kNativeControl.height:
            cls.height = NativeControlPar(cls._get_height, cls._set_height,
                                          kArrInt, f'_{cls_name}_height',
                                          CONTROL_PAR_POS_X)
        cls.height.none_to_dict(self)
        if height:
            self.height = height

    def _get_x(self):
        return self._x

    def _set_x(self, val):
        self._x = val

    def _get_y(self):
        return self._y

    def _set_y(self, val):
        self._y = val

    def _get_width(self):
        return self._width

    def _set_width(self, val):
        self._width = val

    def _get_height(self):
        return self._height

    def _set_height(self, val):
        self._height = val

    @staticmethod
    def get_by_id(_id):
        if isinstance(_id, kInt):
            _id = _id._get_runtime()
        return kNativeControl._controls[_id]

    @property
    def id(self):
        return self._id

    def _generate_executable(self):
        raise NotImplementedError

    @staticmethod
    def _generate_init():
        # print('_generate_init')
        if kNativeControl._init_is_generated:
            return []
        kNativeControl._init_is_generated = True
        out = list()
        for inst in kNativeControl._controls:
            out.extend([inst._get_init_line(),
                        f'{inst._id._get_compiled()} := get_ui_id' +
                        f'({inst._var._get_compiled()})'])
        subclasses = [kNativeControl]
        subclasses.extend(_all_subclasses(kNativeControl))

        for cls in subclasses:
            if not hasattr(cls, '_ids'):
                continue
            # print(f'generating params for {cls}')
            arrays = dict()
            params = dict()
            # print('items in dict:')
            for key, val in cls.__dict__.items():
                # print(f'key={key}, val={val}')
                if isinstance(val, NativeControlPar) and \
                        val.assigned:
                    arrays[key] = val.init_array()
                    params[key] = val.control_par
            Output().set(out)
            for arr in arrays.values():
                for line in arr._generate_init():
                    Output().put(line)
                arr._generate_init = lambda: []
            with For(len(cls._ids)) as seq:
                for idx in seq:
                    for par, arr in arrays.items():
                        arr_val = arr[idx]
                        with If(arr_val != kNone()):
                            check()
                            params[par].set(cls._ids[idx], arr_val)
            Output().release()
        return out

    @abstractmethod
    def _get_init_line(self):
        pass

    def _get_compiled(self):
        return self._var._get_compiled()

    def _set_compiled(self, value):
        return self._var._set_compiled(value)

    def name(self):
        return self._var.name()

    def _get_runtime(self):
        return self._var._get_runtime()

    def _set_runtime(self, value):
        return self._var._set_runtime(value)

    def __getitem__(self, idx):
        return self._var.__getitem__(idx)

    def __setitem__(self, idx, value):
        return self._var.__setitem__(idx, value)

    def iter_runtime(self):
        return self._var.iter_runtime()

    def iter_runtime_fast(self):
        return self._var.iter_runtime_fast()


class ControlPar(BuiltIn):

    def __init__(self, par_name: str, control_attr_name: str):
        self._attr_name = control_attr_name
        super().__init__(f'CONTROL_PAR_{par_name}')

    def set(self, control_id: int, value: int):
        control = kNativeControl.get_by_id(control_id)
        cls = control.__class__
        attr = getattr(cls, self._attr_name)
        attr.set_raw(control, value)
        # setattr(control, self._attr_name, value)
        if hasattr(value, '_get_compiled'):
            value = value._get_compiled()
        Output().put(
            f'set_control_par({control_id._get_compiled()}, ' +
            f'{self._get_compiled()}, {value})')


CONTROL_PAR_POS_X = ControlPar('POS_X', 'x')
