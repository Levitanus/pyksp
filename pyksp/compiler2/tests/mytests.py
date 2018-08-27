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
from k_built_ins import BuiltInID
# from functions import Function


class DevTest(t.TestCase):

    def setUp(self):
        KspObject.refresh()
        Output().refresh()
        IName.refresh()
        Callback.refresh()
        # Function.refresh()
        BuiltInID.refresh()
        refresh_names_count()
        KSP.refresh()

    def tearDown(self):
        KspObject.refresh()
        Output().refresh()
        IName.refresh()
        Callback.refresh()
        # Function.refresh()
        BuiltInID.refresh()
        refresh_names_count()
        KSP.refresh()
