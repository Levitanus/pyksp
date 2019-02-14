import typing as ty

from .service import KTest
from .. import service_types as st
from .. import base_types as bt
from .. import abstract as ab


# CPD-OFF
@st.vrs
def simple_func(arg1: int,
                *,
                arg2: st.Loc[int],
                arg3: st.Loc[str,
                             6]) -> ty.Tuple[int,
                                             st.LocInt,
                                             st.LocArrStr]:
    return arg1, arg2, arg3


# CPD-ON


class SimpleClass:
    @st.vrs
    def simple_method(
        self,
        arg1: int,
        *,
        arg2: st.Loc[int],
        arg3: st.Loc[str,
                     6]
    ) -> ty.Tuple[int,
                  st.LocInt,
                  st.LocArrStr]:
        return arg1, arg2, arg3


class TestVrs(KTest):
    def runTest(self) -> None:
        f_ret = simple_func(5)
        m_ret = SimpleClass().simple_method(4)
        self.assertIsInstance(f_ret[0], int)
        self.assertIsInstance(f_ret[1], bt.Var[int])
        self.assertIsInstance(f_ret[2], bt.Var[str, 6])
        self.assertIsInstance(m_ret[0], int)
        self.assertIsInstance(m_ret[1], bt.Var[int])
        self.assertIsInstance(m_ret[2], bt.Var[str, 6])
        self.assertEqual(
            f_ret[1].name(),
            '$pyksp_tests_test_service_types_simple_func_arg2'
        )
        self.assertEqual(
            f_ret[2].name(),
            '!pyksp_tests_test_service_types_simple_func_arg3'
        )
        self.assertEqual(
            m_ret[1].name(),
            '$pyksp_tests_test_service_types_SimpleClass_simple_method_arg2'
        )
        self.assertEqual(
            m_ret[2].name(),
            '!pyksp_tests_test_service_types_SimpleClass_simple_method_arg3'
        )
        self.assertTrue(simple_func(5))

        self.assertTrue(issubclass(st.In[int], bt.Var[int]))
        self.assertTrue(issubclass(st.In[int], st.InInt))
        self.assertTrue(issubclass(st.In[int, 5], bt.ArrInt))
        self.assertTrue(issubclass(st.In[int, 5], st.InArrInt))

        self.assertTrue(issubclass(st.In[str], bt.Var[str]))
        self.assertTrue(issubclass(st.In[str], st.InStr))
        self.assertTrue(issubclass(st.In[str, 5], bt.ArrStr))
        self.assertTrue(issubclass(st.In[str, 5], st.InArrStr))

        self.assertTrue(issubclass(st.In[float], bt.Var[float]))
        self.assertTrue(issubclass(st.In[float], st.InFloat))
        self.assertTrue(issubclass(st.In[float, 5], bt.ArrFloat))
        self.assertTrue(issubclass(st.In[float, 5], st.InArrFloat))

        self.assertTrue(issubclass(st.Out[int], bt.Var[int]))
        self.assertTrue(issubclass(st.Out[int], st.OutInt))
        self.assertTrue(issubclass(st.Out[int, 5], bt.ArrInt))
        self.assertTrue(issubclass(st.Out[int, 5], st.OutArrInt))

        self.assertTrue(issubclass(st.Out[str], bt.Var[str]))
        self.assertTrue(issubclass(st.Out[str], st.OutStr))
        self.assertTrue(issubclass(st.Out[str, 5], bt.ArrStr))
        self.assertTrue(issubclass(st.Out[str, 5], st.OutArrStr))

        self.assertTrue(issubclass(st.Out[float], bt.Var[float]))
        self.assertTrue(issubclass(st.Out[float], st.OutFloat))
        self.assertTrue(issubclass(st.Out[float, 5], bt.ArrFloat))
        self.assertTrue(issubclass(st.Out[float, 5], st.OutArrFloat))


class TestSubArray(KTest):
    def runTest(self) -> None:
        arr = bt.ArrInt([1, 3, 4, 6, 7], name='arr')
        s_arr = st.SubArray(arr, 1, 3)
        self.assertEqual(s_arr.val[0], 3)
        self.assertEqual(s_arr.val[2], 6)
        with self.assertRaises(IndexError):
            s_arr.val[3]  # pylint: disable=W0104

        self.assertEqual(s_arr[0].name(), '%arr[1]')
        self.assertEqual(s_arr[2].name(), '%arr[3]')
        idx = bt.Var[int](2, name='idx')
        self.assertEqual(s_arr[idx].name(), '%arr[1 + $idx]')
        self.assertEqual(s_arr[idx].val, 6)
        self.assertEqual(s_arr[-idx].name(), '%arr[3 + -$idx]')
        self.assertEqual(s_arr[-idx].val, 3)

        out = ab.KSP.new_out()
        val = bt.Var[int](12, name='val')
        s_arr[idx] = val
        self.assertEqual(s_arr[idx].name(), '%arr[1 + $idx]')
        self.assertEqual(s_arr[idx].val, 12)
        self.assertEqual(arr[3].val, 12)
        self.assertEqual(out.get()[-1].line, '%arr[1 + $idx] := $val')

        s_arr.set_val_at_idx(1, 24)
        self.assertEqual(arr.val[2], 24)
        with self.assertRaises(TypeError):
            s_arr.val = [1, 2, 3, 4, 5]
        s_arr.val = [7, 6, 5]
        self.assertEqual(arr.val[1:4], [7, 6, 5])
        self.assertEqual(arr.val[3], 5)
        self.assertIsInstance(s_arr, bt.Arr[int, 3])
