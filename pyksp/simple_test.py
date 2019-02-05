from . import service_types as st


@st.vrs
def st_func(arg: int, *, arg1: st.Loc[str, 5]) -> None:
    print(arg, f'{arg1.name()}:{arg1.val}')
    # arg1[3] <<= 'f'  # type: ignore


class C:
    @st.vrs
    def st_method(self, arg: int, *, arg1: st.Loc[str, 5]) -> None:
        print(self, arg, f'{arg1.name()}:{arg1.val}')


st_func(1)
c = C()
c.st_method(3)
c.st_method(5)
