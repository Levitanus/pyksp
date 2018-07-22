import os.path
import sys
import re
import time

import callbacks_generated as on
import callbacks as cb
from abstract import KspObject
from interfaces import IOutput

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ksp_compiler3'))
from ksp_compiler3 import ksp_compiler


class Script:
    '''
    Main class providing compilation.
    Has to be unique per main module

    Usage:
        script = Script(file-name, [name=None, width=None, height=None,
             skin_offset=None, use_nils=True])
        script.compile([insert_comments])
    '''

    def __init__(self, file_name, name=None, width=None, height=None,
                 skin_offset=None, use_nils=True):
        self.file = file_name
        self.name = name
        self.width = width
        use_width = True
        if width is None:
            self.width = 633
            use_width = False
        assert(self.width >= 633), 'width can not be less than 633px'
        self.height = height
        use_height = True
        if height is None:
            use_height = False
            assert(int(skin_offset) == skin_offset),\
                'skin_offset has to be int'
            assert(skin_offset >= 0), 'skin_offset can not be less than 0'
        self.skin_offset = skin_offset
        self.use_nils = use_nils

        self.init_lines = self._initialize(use_width, use_height)

    def _initialize(self, use_width, use_height):
        code = list()
        if self.name is not None:
            code.append('set_script_title("%s")' % self.name)
        if use_width is True:
            code.append('set_ui_width_px(%s)' % self.width)
        if use_height is True:
            code.append('set_ui_height_px(%s)' % self.height)
        if self.skin_offset is not None:
            code.append('set_skin_offset(%s)' % self.skin_offset)

        return code

    def compile(self, insert_comments=False):
        KspObject.comments = insert_comments

        code = list()
        code.append('on init')
        code.extend(KspObject.generate_init())
        code.extend(on.init.generate_code())
        code.extend(self.init_lines)
        code.append('end on')
        code.extend(cb.Callbacks.generate_code())
        code.extend(KspObject.generate_executable())

        code = self._prepare_code(code)

        if self.use_nils is True:
            code = self._get_nils_code(code)
        else:
            localtime = time.asctime(time.localtime(time.time()))
            code = "{ Compiled on " + localtime + " }\n" \
                + code
        if not os.path.isabs(self.file):
            self.file = os.path.join(
                os.path.dirname(__file__), self.file)
        if not re.search(r'\.txt$', self.file):
            self.file += '.txt'

        f = open(self.file, 'w')
        f.writelines(code)
        f.close()
        self.compiled_code = code

    def _get_nils_code(self, code):

        compiler = \
            ksp_compiler.KSPCompiler(code,
                                     optimize=True,
                                     extra_syntax_checks=True,
                                     check_empty_compound_statements=True)
        compiler.compile()
        code = compiler.compiled_code
        # print(code)
        # assert (compiler.output_file), 'there is no code'
        return code

    def _prepare_code(self, code):
        newcode = ''
        for line in code:
            if line[-1] != '\n':
                line += '\n'
            newcode += line
        return newcode


if __name__ == '__main__':
    script = Script('myscript', name='MyScriptTitle',
                    width=800, height=150,
                    skin_offset=20, use_nils=False)

    @on.init
    def foo():
        IOutput.put('message("Hello World!")')

    script.compile()
    print(script.compiled_code)
