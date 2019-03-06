from .service import KTest

from .. import base_types as bt
from .. import functions as fn
from .. import service_types as st


@fn.func
def func(arg: int, *, loc: st.Loc[int]) -> None:
    print('function', arg, loc)


@fn.func
def in_out_func(arg: st.In[int], ret: st.Out[int]) -> None:
    ret <<= arg


class TestFunctions(KTest):
    @classmethod
    @fn.func
    def method(
        cls,
        arg: int,
        karg: st.In[str],
        obj: 'TestFunctions'
    ) -> None:
        print('method', cls, arg, f'{karg.name()}:{karg.val}')
        obj.assertEqual(
            karg.name(),
            '!_func_str_arr_[%_func_str_ptr_[$_func_str_idx_ + 1] + 0]'
        )

    def test_arg_amount(self) -> None:
        # pylint: disable=W0612
        with self.assertRaises(TypeError):

            @fn.func
            def not_annotated(arg) -> None:  # type: ignore
                return arg

        with self.assertRaises(TypeError):

            @fn.func
            def no_return():  # type: ignore
                pass

        with self.assertRaises(TypeError):

            @fn.func  # type: ignore
            def bad_return() -> int:
                pass

        # pylint: enable=W0612
        func(1)
        with self.assertRaises(TypeError):
            func(2)
        # pylint: disable=E1120
        with self.assertRaises(TypeError):
            self.method(2)  # type: ignore
        with self.assertRaises(TypeError):
            self.method(2, 4, self)  # type: ignore
        # pylint: enable=E1120
        self.method(2, 'just_string', self)
        self.method(2, bt.Var[str]('var_string'), self)
        assert False

    def test_arg_types(self) -> None:
        outi = bt.Var[int](name='outi')
        in_out_func(5, outi)
        self.assertEqual(outi.val, 5)
        self.assertEqual(outi.name(), '$outi')
