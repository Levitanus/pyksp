cashe = set()


class Test:

    def __init__(self):
        cashe.add(self.method)

    def method(self):
        pass


a = Test()
b = Test()

print(cashe)
