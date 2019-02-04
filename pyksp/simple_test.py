import typing as ty
# import functools as ft
# import inspect as it
# from typing_extensions import Literal
# from pyksp import abstract as ab
from pyksp import base_types as bt

T = ty.TypeVar('T')
F = ty.TypeVar('F', bound=ty.Callable[..., None])
IT = ty.TypeVar('IT', bound=int)


class LocMeta(type):
    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        ...


class Loc(metaclass=LocMeta):
    ...


a = Loc[int]


def vrs(f: F) -> F:
    ...


@vrs
def func(arg: int, *, arg1: Loc[int, 5]) -> None:
    print(arg, arg1.val)
    arg1[3] <<= 'f'  # type: ignore


func(arg=1)
