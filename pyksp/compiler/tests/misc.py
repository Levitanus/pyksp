import os
import sys

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from base_types import KspVar
from base_types import AstBase


class SimpleKspVar(KspVar):

    def __init__(self, name, is_local=False, value=None):
        if is_local is True:
            has_init = False
        else:
            has_init = True
        super().__init__(name, is_local=is_local,
                         has_init=has_init, value=value,
                         ref_type=(KspVar, int, str, float))
        self._compiled = 'compiled'
        self._runtime = None

    def _get_compiled(self):
        super()._get_compiled()
        return self._compiled

    def _get_runtime(self):
        super()._get_runtime()
        return self._runtime

    def _set_runtime(self, val):
        super()._set_runtime(val)
        self._runtime = val

    @property
    def val(self):
        if self.is_compiled():
            return self._get_compiled()
        return self._get_runtime()

    def _generate_executable(self):
        super()._generate_executable()
        return

    def _generate_init(self):
        super()._generate_init()
        return ['generated init']


class ValuebleKspVar(SimpleKspVar):

    def _set_runtime(self, val):
        self._value = val

    def _get_runtime(self):
        return self._value


class SimpleAst(AstBase):

    def expand(self):
        return 'SimpleAst_expanded'
