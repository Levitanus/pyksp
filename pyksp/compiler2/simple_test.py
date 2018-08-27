class Prop:

    def __init__(self, name):
        self._name = name

    def __set__(self, obj, val):
        self.check_attr(obj)
        setattr(obj, f'_{self._name}', val)

    def __get__(self, obj, cls):
        if obj:
            self.check_attr(obj)
            return getattr(obj, f'_{self._name}')
        return self

    def __call__(self, cls):
        setattr(cls, self._name, self)
        return cls

    def check_attr(self, obj):
        if not hasattr(obj, f'_{self._name}'):
            setattr(obj, f'_{self._name}', 0)


has_x = Prop('x')
has_y = Prop('y')


@has_x
class A:
    pass


@has_x
@has_y
class B:
    pass


a = A()
print(a.x)
a.x = 6
print(a.x)

b = B()
print(b.y)
b.x = 4
print(b.x)
