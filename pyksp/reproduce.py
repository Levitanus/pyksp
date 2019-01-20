class A:

    def __add__(self, other) -> int:
        ...

    def __iadd__(self, other) -> 'A':
        ...


class C(A):

    def __iadd__(self, other) -> 'C':
        ...
