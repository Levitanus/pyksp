import unittest as t


class MyOwnTestCase(t.TestCase):

    def assertEqual(self, a, b):
        if isinstance(a == b, bool):
            return super().assertEqual(a, b)
        if callable(a):
            a = a()
        if callable(b):
            b = b()
        return super().assertEqual(a, b)
