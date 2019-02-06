import unittest as ut

from .. import base_types as bt
from .. import abstract as ab
from .. import stack as stc

push_str = """\
%base[$ptr] := $var
$ptr := $ptr + 1
%__for_idx__[0] := 0
while(%__for_idx__[0] < 4)
    %base[$ptr + %__for_idx__[0]] := %arr[%__for_idx__[0]]
    inc(%__for_idx__[0])
end while"""


class TestFrameVar(ut.TestCase):
    def tearDown(self) -> None:
        bt.VarBase.refresh()
        ab.KSP.refresh()
        ab.NameVar.refresh()

    # @ut.skip
    def runTest(self) -> None:
        out = ab.KSP.new_out()
        base = bt.Arr[int](name='base', size=10, local=True)
        ptr = bt.Var[int](name='ptr', local=True)
        var = bt.Var[int](15, name='var', local=True)
        fv = stc.FrameVar(base, var, 1)
        ret_var, idx = fv.push(ptr)
        ptr <<= idx
        self.assertEqual(ret_var.val, 15)
        self.assertEqual(ret_var.name(), '%base[$ptr]')
        self.assertEqual(bt.get_value(base[0]), 15)
        self.assertEqual(bt.get_value(idx), 1)
        self.assertEqual(bt.get_compiled(idx), '$ptr + 1')

        arr = bt.Arr[int]([1, 3, 4, 5], name='arr', local=True)
        fa = stc.FrameVar(base, arr, len(arr))
        ret_arr, idx = fa.push(ptr)
        self.assertEqual(base[2].val, 3)
        self.assertEqual(ret_arr[1].val, 3)
        self.assertEqual(ret_arr[1], 3)
        self.assertIs(base, ret_arr.array)  # type: ignore
        self.assertEqual(ret_arr.val, [1, 3, 4, 5])
        self.assertEqual(bt.get_value(idx), 5)
        self.assertEqual(bt.get_compiled(idx), '$ptr + 4')
        self.assertEqual(out.get_str(), push_str)
