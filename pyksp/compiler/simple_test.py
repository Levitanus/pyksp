class SingletoneMeta(type):

    def __new__(cls, name, bases, dct):
        access = SingletoneMeta.access
        dct['__new__'] = access
        dct['instance'] = None
        class_ = type.__new__(cls, name, bases, dct)
        return class_

    def access(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = cls
            return cls.__init__(cls, *args, **kwargs)
        return cls.instance.__call__(cls, *args, **kwargs)


class Test():
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = cls
            return cls.__init__(cls, *args, **kwargs)
        return cls.instance.__call__(cls, *args, **kwargs)

    def __init__(self, arg):
        print('init')

    def __call__(self, arg):
        print('call')
        return arg


x = Test(1)
y = Test(2)
z = Test(3)

print(x)
print(y)
print(z)
