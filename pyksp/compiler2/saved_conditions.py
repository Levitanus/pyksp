
class test:

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return '%s = %s' % (self.value, other.value)

    def __lt__(self, other):
        return '%s < %s' % (self.value, other.value)

    def __str__(self):
        return self.value


a = test('a')

b = test('b')

c = 8

d = [1, 2, 3, 4, 5, 8, 10]


class Array:
    def __init__(self, name, *args):
        self.name = name
        self.items = args


class For:
    def __init__(self, var, collection):
        self.var = var
        self.name = var.value
        var.value = '%s[%s]' % (collection.name, self.var)
        self._collection = collection
        print('%s := 0' % self.name)
        print('while(%s <= %s)' %
              (self.name, len(self._collection.items) - 1))

    def __call__(self, *body):
        print('inc(%s)' % self.name)
        print('end while')
        self.var = self.name


array = Array('array', 1, 2, 3, 4)


class If:
    count = 0

    def __init__(self, condition):
        If.count += 1
        self.condition = condition
        print('if (%s)' % condition)

    def __call__(self, *body):
        If.count -= 1
        print('end if')


class Else:
    def __init__(self, condition=None):
        if If.count <= 0:
            raise Exception('"If(condition)(..." expected')
        print('else')
        self.condition = condition
        if condition is not None:
            print('if (%s)' % condition)

    def __call__(self, *body):
        if self.condition is not None:
            print('end if')


class Select:
    def __init__(self, variable):
        print('select(%s)' % variable.value)

    def __call__(self, *body):
        print('end select')


class Case:
    def __init__(self, number, tonumber=None):
        string = 'case %s' % number
        if tonumber:
            string += ' to %s' % tonumber
        print(string)

    def __call__(self, *body):
        pass


def message(*args):
    msg = ''
    for idx, val in enumerate(args):
        if isinstance(val, str):
            val = '"%s"' % val
        if idx == len(args) - 1:
            msg += '%s' % val
            break
        msg += '%s & ' % val
    print('message(%s)' % msg)


If(a < b)(
    message('inside if'),
    Else(a == b)(
        message('c is in d at index %s' % d.index(c))
    )
)
print('--------\n')

If(a < b)(
    message('inside if'),
    Else()(
        message('inside else')
    )
)
print('--------\n')

Select(a)(
    Case(1)(
        message('inside case %s' % 1)
    ),
    Case(2, 4)(
        message('inside case %s to %s' % (2, 4))
    )
)
print('--------\n')

For(a, array)(
    message(a)
)
