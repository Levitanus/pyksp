import typing as ty
import typing_extensions as te
from abc import ABCMeta


# def class_decorator(cls):
#     anno = get_type_hints(cls)  # raises NameError on 'C'
#     print(f'Annotations for {cls}: {anno}')
#     return cls


# @class_decorator
# class C:
#     singleton: 'C' = None

T = ty.TypeVar('T')


T1 = ty.TypeVar('T1', int, str)
T2 = ty.TypeVar('T2', int, str)

TU = ty.Union[ty.List[T1], ty.Tuple[T1]]


class A(ty.Generic[T]):
    # __args are unique every instantiation
    __args: ty.ClassVar[ty.Optional[ty.Tuple[ty.Type[T]]]] = None
    value: T

    def __init__(self, value: ty.Optional[T]=None) -> None:
        """Get actual type of generic and initizalize it's value."""
        cls = ty.cast(ty.Type[A], self.__class__)
        if cls.__args:
            self.ref = cls.__args[0]
        else:
            self.ref = type(value)
        if value:
            self.value = value
        else:
            self.value = self.ref()
        cls.__args = None

    def __class_getitem__(cls, *args: ty.Union[ty.Type[int], ty.Type[str]]
                          ) -> ty.Type['A']:
        """Recive type args, if passed any before initialization."""
        cls.__args = ty.cast(ty.Tuple[ty.Type[T]], args)
        return super().__class_getitem__(*args)  # type: ignore


a = A[int]()
b = A(int())
c = A[str]()
print([a.value, b.value, c.value])  # [0, 0, '']
