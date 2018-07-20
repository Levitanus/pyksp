from abc import abstractmethod
from abc import ABCMeta


class Parent1:
    def method(self):
        print('Parent1, val =', self.val)


class Parent2:
    def method(self):
        print(f'Parent2, val = "{self.val}"')


class A(Parent1, Parent2):
    def __init__(self, val):
        if isinstance(val, int):
            self.type = Parent1
        if isinstance(val, str):
            self.type = Parent2
        self.val = val

    def method(self):
        print(self.type)
        # self.type.method(self)
        super(self.type, self).method()


obj = A(1)
obj.method()
