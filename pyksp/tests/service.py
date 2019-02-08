import unittest as ut
from .. import abstract as ab
from .. import base_types as bt


class KTest(ut.TestCase):
    def tearDown(self) -> None:
        bt.VarBase.refresh()
        ab.KSP.refresh()
        ab.NameVar.refresh()

    def setUp(self) -> None:
        self.out = ab.KSP.new_out()
