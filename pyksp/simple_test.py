import typing as ty
# import functools as ft
# import inspect as it
# from typing_extensions import Literal
# from pyksp import abstract as ab
# from pyksp import base_types as bt
from . import service_types as st

T = ty.TypeVar('T')
F = ty.TypeVar('F', bound=ty.Callable[..., None])
IT = ty.TypeVar('IT', bound=int)


def vrs(f: F) -> F:
    ...


@vrs
def func(arg: int, *, arg1: st.Loc[int, 5]) -> None:
    print(arg, arg1.val)
    arg1[3] <<= 'f'  # type: ignore


# func(1)
