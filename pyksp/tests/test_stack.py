from .service import KTest

from .. import base_types as bt
from .. import stack as stc
from .. import service_types as st


class TestStackArray(KTest):
    def runTest(self) -> None:
        s_arr = stc.StackArray('test', bt.ArrStr)

        s_arr._check_init()
        self.assertIsInstance(s_arr.array, bt.Arr[str, 32768])
        self.assertIsInstance(s_arr.idx, bt.Var[int])
        self.assertIsInstance(s_arr.ptr, bt.Arr[int, 100])


push_str = '''\
%_test_int_arr_[%_test_int_ptr_[$_test_int_idx_ + 1] + 0] := $iv
%__for_idx__[0] := 0
while(%__for_idx__[0] < 4)
    %_test_int_arr_[%_test_int_ptr_[$_test_int_idx_ + 1] + 2 + \
%__for_idx__[0]] := %ia[%__for_idx__[0]]
    inc(%__for_idx__[0])
end while
?_test_float_arr_[%_test_float_ptr_[$_test_float_idx_ + 1] + 0] := 6.2
inc($_test_int_idx_)
%_test_int_ptr_[$_test_int_idx_ + 1] := %_test_int_ptr_[$_test_int_idx_] + 11
inc($_test_str_idx_)
%_test_str_ptr_[$_test_str_idx_ + 1] := %_test_str_ptr_[$_test_str_idx_] + 1
inc($_test_float_idx_)
%_test_float_ptr_[$_test_float_idx_ + 1] := \
%_test_float_ptr_[$_test_float_idx_] + 1
dec($_test_int_idx_)
dec($_test_str_idx_)
dec($_test_float_idx_)'''


class TestStack(KTest):
    def runTest(self) -> None:
        stack = stc.Stack('test')
        iv = bt.Var[int](name='iv')
        il = st.Loc[int]
        ia = bt.Arr[int]([1, 3, 4, 7], name='ia')
        ial = st.Loc[int, 5]
        sl = st.Loc[str]
        rp = 6.2

        riv, ril, ria, rial, rsl, rrp = stack.push(
            iv, il, ia, ial, sl, rp
        )
        self.assertEqual(
            riv.name(),
            '%_test_int_arr_[%_test_int_ptr_[$_test_int_idx_ + 1] + 0]'
        )
        self.assertEqual(
            ril.name(),
            '%_test_int_arr_[%_test_int_ptr_[$_test_int_idx_ + 1] + 1]'
        )
        self.assertEqual(
            ria[0].name(),
            '%_test_int_arr_[%_test_int_ptr_[$_test_int_idx_ + 1] + 2 + 0]'
        )
        self.assertEqual(
            rial[0].name(),
            '%_test_int_arr_[%_test_int_ptr_[$_test_int_idx_ + 1] + 6 + 0]'
        )
        self.assertEqual(
            rsl.name(),
            '!_test_str_arr_[%_test_str_ptr_[$_test_str_idx_ + 1] + 0]'
        )
        self.assertEqual(
            rrp.name(),
            '?_test_float_arr_[%_test_float_ptr_[$_test_float_idx_ + 1] + 0]'
        )

        frame = stack.pop()
        self.assertEqual(frame, {int: 11, str: 1, float: 1})
        self.assertEqual(self.out.get_str(), push_str)
