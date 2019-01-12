import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from abstract import KspObject
from abstract import Output
from abstract import IName
from abstract import KSP

from native_types import refresh_names_count
from k_built_ins import Callback
from k_built_ins import BuiltIn
# from functions import Function
from bi_ui_controls import refresh as gui_refresh
from conditions_loops import For


class DevTest(t.TestCase):

    def setUp(self):
        KspObject.refresh()
        Output().refresh()
        Callback.refresh()
        # Function.refresh()
        BuiltIn.refresh()
        refresh_names_count()
        IName.refresh()
        gui_refresh()
        For.refresh()
        KSP.refresh()

    def tearDown(self):
        KspObject.refresh()
        Output().refresh()
        Callback.refresh()
        # Function.refresh()
        BuiltIn.refresh()
        refresh_names_count()
        IName.refresh()
        gui_refresh()
        For.refresh()
        KSP.refresh()
