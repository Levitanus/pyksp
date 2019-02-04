import typing as ty
import functools as ft
import inspect as it
import re
if __name__ == '__main__':
    __name__ = 'pyksp.simple_test'
# from typing_extensions import Literal
from pyksp import abstract as ab
# from pyksp import base_types as bt
from . import service_types as st

T = ty.TypeVar('T')
F = ty.TypeVar('F', bound=ty.Callable[..., None])
IT = ty.TypeVar('IT', bound=int)


def vrs(f: F) -> F:
    name = f.__qualname__
    name = re.sub(r'\.', '_', name)
    ab.NameVar.scope(name)
    sig = it.signature(f)
    new_kwargs: ty.Dict[str, st.Loc] = dict()
    for par in sig.parameters:
        anno = sig.parameters[par].annotation
        # print(par, anno)
        if issubclass(anno, st.Loc):
            # print('instance')
            a_kwgs = dict(name=par)
            if hasattr(anno, 'size'):
                a_kwgs['size'] = anno.size
            try:
                new_kwargs[par] = anno(**a_kwgs)
            except NameError:
                new_kwargs[par] = anno(**a_kwgs, local=True)
    ab.NameVar.scope()

    @ft.wraps(f)
    def wrapper(*args: ty.Any, **kwargs: ty.Any) -> None:
        b_args = sig.bind(*args, **kwargs, **new_kwargs)
        return f(*b_args.args, **b_args.kwargs)

    return ty.cast(F, wrapper)


@vrs
def func(arg: int, *, arg1: st.Loc[str, 5]) -> None:
    print(arg, f'{arg1.name()}:{arg1.val}')
    # arg1[3] <<= 'f'  # type: ignore


class C:
    @vrs
    def method(self, arg: int, *, arg1: st.Loc[str, 5]) -> None:
        print(arg, f'{arg1.name()}:{arg1.val}')


func(1)  # pylint: disable=E1125
c = C()
c.method(3)  # pylint: disable=E1125
c.method(5)  # pylint: disable=E1125
