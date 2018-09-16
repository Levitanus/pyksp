import time
import os
import sys
import textwrap
import codecs
import pyperclip

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
    '''clears the Output()
    calls refresh methods of:
    BuiltIn
    IName
    For
    KSP
    calls native_types.refresh_names_count()
    and bi_ui_controls.refresh()
    '''
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
    '''Is used for generating code of all API calls used in project.
    All KSP objects, attempted to appear in code has to be placed inside
    script main method.

    args:
    - out_file can be as str filename with .txt ending as well as
        Kscript.clipboard
    if filename is not full path, the __main__.__file__ path will be used.
    if out_file is Kscript.clipboard, compiled code will be copied to the
        exchange buffer

    - title is script title to be set via set_script_title() func

    -if compact is True, all variable names will be hashed

    - with max_line_length being not None, lines with
        length > max_line_length will be wrapped to fit it.
        currently, lines with "quoted strings" are not wrapped

    - indents and docstrings are out of work

    Example:
    script = kScript(r'C:/file.txt',
                         'myscript', max_line_length=70, compact=True)
    def foo():
        mw = kMainWindow()
        buttons_area = kWidget(parent=mw)
        buttons_area.place_pct(20, 10, 50, 80)
        ba_bg = kLabel(parent=buttons_area)
        ba_bg.pack(sticky='nswe')
        ba_bg.text <<= ''
    script.main = foo
    script.compile()
    '''
    clipboard = object()

    def __init__(self, out_file: str, title: str=None,
                 compact=False, max_line_length=79,
                 indents=False,
                 docstrings=False) -> None:
        if out_file is self.clipboard:
            self._file = out_file
        else:
            self._file = os.path.normpath(out_file)
        self._compact = compact
        self._title = title
        self._line_length = max_line_length

    def _generate_code(self):
        print('generating code')
        refresh_all()
        KSP.set_compiled(True)
        KSP.in_init(True)
        if self._compact:
            IName.set_compact(True)
        # try:
        self.main()
        # except AttributeError:
        #     raise RuntimeError(
        #         '''all KSP objects attemped to appear in the code
        #         has to be placed inside function, which is assigned
        #         to script main attribute''')
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
        print('getting lines of regular operations')
        regular = Output().get()
        print('getting inits of declared objects')
        obj_init = KspObject.generate_all_inits()
        print('getting inits of NativeControls params')
        ctrls = KspNativeControlMeta.generate_init_code()
        print('getting lines of init callback, pasted as decorated funcs')
        init_cb = InitCallback.generate_body()[1:-1]
        KSP.in_init(False)
        print('generating other callbacks')
        cbs = Callback.get_all_bodies()
        print('generating functions bodies')
        funcs = list()
        for f in Function._functions.values():
            funcs = f._generate_executable()
            break
        # funcs = KspObject.generate_all_executables()
        out = list()
        print('joining the code')
        localtime = time.asctime(time.localtime(time.time()))
        out.append('{ Compiled on %s }' % localtime)
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
        print('wrapping long lines')
        out = self._check_length(out)

        KSP.set_compiled(False)
        print('sucsessfully generated')
        return out

    def _check_length(self, lines):
        if self._line_length is False:
            return lines
        new_lines = list()
        for line in lines:
            line = line.strip()
            if len(line) <= self._line_length:
                new_lines.append(line)
                continue
            if line.find('"') > -1:
                new_lines.append(line)
                continue
            new_lines.extend(self.wrap(line, self._line_length))
        return new_lines

    def wrap(self, s, w):
        new = textwrap.wrap(s, w, break_long_words=False,
                            subsequent_indent='    ')
        for idx in range(len(new) - 1):
            new[idx] += '...'
        new[-1]
        return new

    def compile(self):
        print(f'compiling the script {self}')
        code = self._generate_code()
        newcode = ''
        for line in code:
            newcode += line + '\n'
        if self._file is self.clipboard:
            print(f'saved compiled script {self} to clipboard')
            pyperclip.copy(newcode)
            return

        def main_is_frozen():
            return (hasattr(sys, "frozen") or  # new py2exe
                    hasattr(sys, "importers"))

        def get_main_dir():
            if main_is_frozen():
                return os.path.dirname(sys.executable)
            return os.path.dirname(sys.argv[0])

        if not os.path.isabs(self._file):
            self._file = os.path.join(get_main_dir(), self._file)
        with codecs.open(self._file, 'w', encoding='latin-1') as output:
            if output:
                output.write(newcode)
        print(f'saved compiled script {self} to {self._file}')
