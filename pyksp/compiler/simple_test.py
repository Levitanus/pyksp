

class Stack:
    stack = list()

    @staticmethod
    def append(seq):
        Stack.stack.append(seq)

    @staticmethod
    def put(func):
        for item in Stack.stack:
            item.add(func)

    @staticmethod
    def pop():
        Stack.stack.pop()


class Handle:

    _instances = list()

    def __init__(self, func):
        self.func = func
        self.stack = set()
        Handle._instances.append(self)

    def __call__(self, **kwargs):
        Stack.put(self)
        Stack.append(self.stack)

        out = self.func(**kwargs)

        if self in self.stack:
            raise Exception(f'recursive call of {self} detected')
        Stack.pop()
        return out

    @staticmethod
    def sort():
        new = list()
        for instance in Handle._instances:
            if len(instance.stack) == 0:
                new.append(instance)
                continue
            if instance in instance.stack:
                raise Exception('recursion detected')
            for func in instance.stack:
                if func not in new:
                    new.append(func)
                    Handle._instances.remove(func)
                continue
            new.append(instance)

        Handle._instances = new


@Handle
def foo():
    pass


@Handle
def foo2(exit=False):
    if exit:
        return
    Simple.foo1()


class Simple:

    @staticmethod
    @Handle
    def foo1():
        foo()
        # foo2(exit=True)


Simple.foo1()
foo2()

print([inst.stack for inst in Handle._instances])
print([inst for inst in Handle._instances])

Handle.sort()

print('\nsorted:')
print([inst.stack for inst in Handle._instances])
print([inst for inst in Handle._instances])

print(Stack.stack)
