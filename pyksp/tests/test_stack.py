from .service import KTest

from .. import base_types as bt
from .. import stack as stc

push_str = """\
%base[$ptr] := $var
inc($ptr)
%__for_idx__[0] := 0
while(%__for_idx__[0] < 4)
    %base[$ptr + %__for_idx__[0]] := %arr[%__for_idx__[0]]
    inc(%__for_idx__[0])
end while"""


class TestFrameVar(KTest):

    # @ut.skip
    def runTest(self) -> None:
        base = bt.Arr[int](name='base', size=10, local=True)
        ptr = bt.Var[int](name='ptr', local=True)
        var = bt.Var[int](15, name='var', local=True)
        fv = stc.FrameVar(base, var, 1)
        ret_var = fv.push(ptr)
        ptr.inc()
        self.assertEqual(ret_var.val, 15)
        self.assertEqual(ret_var.name(), '%base[$ptr]')
        self.assertEqual(bt.get_value(base[0]), 15)

        arr = bt.Arr[int]([1, 3, 4, 5], name='arr', local=True)
        fa = stc.FrameVar(base, arr, len(arr))
        ret_arr = fa.push(ptr)
        self.assertEqual(base[2].val, 3)
        self.assertEqual(ret_arr[1].val, 3)
        self.assertEqual(ret_arr[1], 3)
        self.assertIs(base, ret_arr.array)  # type: ignore
        self.assertEqual(ret_arr.val, [1, 3, 4, 5])
        self.assertEqual(self.out.get_str(), push_str)


class TestStackArray(KTest):
    def runTest(self) -> None:
        s_arr = stc.StackArray('test', bt.ArrStr)

        s_arr._check_init()
        self.assertIsInstance(s_arr.array, bt.Arr[str, 32768])
        self.assertIsInstance(s_arr.idx, bt.Var[int])
        self.assertIsInstance(s_arr.ptr, bt.Arr[int, 100])
        s_arr.push(5)
        self.assertEqual(s_arr.ptr[1], 5)
        self.assertEqual(s_arr.idx, 0)
        sfv = stc.FrameVar(s_arr.array, bt.VarStr('a'), 1)
        r_var = sfv.push(s_arr.ptr[s_arr.idx])
        sfa = stc.FrameVar(s_arr.array, bt.ArrStr(['b', 'c', 'd', 'e']), 4)
        r_arr = sfa.push(s_arr.ptr[s_arr.idx + 1])
        self.assertEqual(r_var.val, 'a')
        self.assertEqual(r_var.name(), '!_test_arr_[%_test_ptr_[$_test_idx_]]')

        self.assertEqual(r_arr[0].val, 'b')
        self.assertEqual(r_arr[0].name(),
                         '!_test_arr_[%_test_ptr_[$_test_idx_ + 1] + 0]')
        self.assertIs(s_arr.array[0]._value, r_var._value)
        self.tearDown()
        self.setUp()
        s_arr.push(1)
        self.assertIsNot(s_arr.array[0]._value, r_var._value)


class TestStack(KTest):
    def runTest(self) -> None:
        stack = stc.Stack('test')
        print(stack.arrays)
        assert False
