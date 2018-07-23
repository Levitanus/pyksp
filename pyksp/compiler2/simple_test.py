
class Test:

    def __init__(self, val, name):
        self._val = val
        self._name = name
        self.named = False

    def __ilshift__(self, other):
        if hasattr(other, 'val'):
            other = other.val
        self.set(other)
        return self

    def __rlshift__(self, other):
        return self.get()

    def set(self, val):
        self._val = val

    def get(self):
        if self.named:
            return self._name
        return self._val

    @property
    def val(self):
        return self._val


x = Test(1, 'x')
y = Test(2, 'y')

print('x.val =', x.val)
print('y.val =', y.val)

x <<= y
print('x.val =', x.val)
z: int = None
z <<= x
print('z =', z)
x <<= 3
y <<= x
print('y.val =', y.val)
y.val = 4
