from abstract import KspObject
from abstract import Output
from abstract import IName
from abstract import KSP

from native_types import refresh_names_count
from k_built_ins import Callback
from k_built_ins import InitCallback
from callbacks import persistence_changed
from k_built_ins import BuiltIn
# from functions import Function
from bi_ui_controls import refresh as gui_refresh
from conditions_loops import For
from functions import Function
from functions import FuncStack
from bi_ui_controls import KspNativeControlMeta
from bi_misc import kLog


def refresh_all():
    KspObject.refresh()
    # Callback.refresh()
    # Function.refresh()
    BuiltIn.refresh()
    refresh_names_count()
    IName.refresh()
    gui_refresh()
    For.refresh()
    Output().refresh()
    KSP.refresh()
    # FuncStack().refr()


class kScript:

    def __init__(self, out_file: str, title: str=None,
                 compact=False, indents=False,
                 docstrings=False) -> None:
        self._file = out_file
        self._compact = compact
        self._title = title

    def _generate_code(self):
        refresh_all()
        KSP.set_compiled(True)
        KSP.in_init(True)
        if self._compact:
            IName.set_compact(True)
        try:
            self.main()
        except AttributeError:
            raise RuntimeError(
                '''all KSP objects attemped to appear in the code
                has to be placed inside function, which is assigned
                to script main attribute''')
        # FuncStack().refr()
        try:
            kLog()
            if kLog()._path:
                KSP.in_init(False)
                persistence_changed(kLog()._log_arr_pers)
                KSP.in_init(True)
        except TypeError as e:
            if str(e).startswith('__init__()'):
                pass
            else:
                raise e
        regular = Output().get()
        obj_init = KspObject.generate_all_inits()
        ctrls = KspNativeControlMeta.generate_init_code()
        init_cb = InitCallback.generate_body()[1:-1]
        KSP.in_init(False)
        cbs = Callback.get_all_bodies()
        for f in Function._functions.values():
            funcs = f._generate_executable()
            break
        # funcs = KspObject.generate_all_executables()
        out = list()
        out.append('on init')
        if self._title:
            out.append(f'set_script_title("{self._title}")')
        out.extend(FuncStack()._init_lines)
        out.extend(obj_init)
        out.extend(ctrls)
        out.extend(regular)
        out.extend(init_cb)
        out.append('end on')

        out.extend(funcs)
        out.extend(cbs)

        KSP.set_compiled(False)
        return out

    def compile(self):
        pass
