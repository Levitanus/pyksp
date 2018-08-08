import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from abstract import KspObject
from abstract import Output
from abstract import IName
from abstract import KSP


class DevTest(t.TestCase):

    def setUp(self):
        KSP.refresh()
        KspObject.refresh()
        Output().refresh()
        IName.refresh()

    def tearDown(self):
        KSP.refresh()
        KspObject.refresh()
        Output().refresh()
        IName.refresh()
