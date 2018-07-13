import unittest as t

from native_types import kInt
from native_types import kArrInt

from abstract import KSP

from dev_tools import DevTest


class FrameVar:

    def __init__(self, name, val, start_idx=None, length=None):
        self.val = val
        self.name = name
        if length:
            self.len = length
            return
        try:
            self.len = len(val)
        except TypeError:
            self.len = 1


class TestFrameVar(DevTest):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_code(self):
        KSP.toggle_test_state(False)
        self.main()

    def test_vars(self):
        KSP.toggle_test_state(True)
        self.main()

    def main(self):
        pass


if __name__ == '__main__':
    t.main()
