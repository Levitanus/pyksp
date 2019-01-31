import typing as ty

T = ty.TypeVar('T', int, ty.List[int])


def foo(arg: T):
    s: T
    t: int

    if not isinstance(s, ty.List):
        t = s  # Incompatible types in assignment
        # (expression has type "List[int]", variable has type "int")
        s = ty.cast(s, int)  # Redundant cast to s?
        t = s
