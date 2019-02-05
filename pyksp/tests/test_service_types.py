import unittest as ut
import typing as ty

from .. import service_types as st
from .. import base_types as bt
from .. import abstract as ab


@st.vrs
def simple_func(arg1: int, *, arg2: st.Loc[int], arg3: st.Loc[str, 6]
                ) -> ty.Tuple[int, st.LocInt, st.LocArrStr]:
    return arg1, arg2, arg3


class SimpleClass:
    @st.vrs
    def simple_method(
            self, arg1: int, *, arg2: st.Loc[int],
            arg3: st.Loc[str, 6]) -> ty.Tuple[int, st.LocInt, st.LocArrStr]:
        return arg1, arg2, arg3


class TestVrs(ut.TestCase):
    def tearDown(self) -> None:
        bt.VarBase.refresh()
        ab.KSP.refresh()
        ab.NameVar.refresh()

    def runTest(self) -> None:
        f_ret = simple_func(5)
        m_ret = SimpleClass().simple_method(4)
        self.assertIsInstance(f_ret[0], int)
        self.assertIsInstance(f_ret[1], bt.Var[int])
        self.assertIsInstance(f_ret[2], bt.Var[str, 6])
        self.assertIsInstance(m_ret[0], int)
        self.assertIsInstance(m_ret[1], bt.Var[int])
        self.assertIsInstance(m_ret[2], bt.Var[str, 6])
        self.assertEqual(f_ret[1].name(),
                         '$pyksp_tests_test_service_types_simple_func_arg2')
        self.assertEqual(f_ret[2].name(),
                         '!pyksp_tests_test_service_types_simple_func_arg3')
        self.assertEqual(
            m_ret[1].name(),
            '$pyksp_tests_test_service_types_SimpleClass_simple_method_arg2')
        self.assertEqual(
            m_ret[2].name(),
            '!pyksp_tests_test_service_types_SimpleClass_simple_method_arg3')
        self.assertTrue(simple_func(5))
