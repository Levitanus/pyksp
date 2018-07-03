import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
import callbacks_generated as on
# import callbacks as cb
from interfaces import IOutput


class TestCallback(t.TestCase):

    def test_init(self):

        @on.init
        def foo():
            IOutput.put("i'm here")

        self.assertEqual(on.init.code[0], "i'm here")

    def test_refresh(self):

        @on.init
        def foo():
            IOutput.put("another here")

        on.init.refresh()

        self.assertEqual(on.init.code, [])


if __name__ == '__main__':
    t.main()
