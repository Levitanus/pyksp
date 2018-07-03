from local_types import kLocInt
from local_types import kLocStr
from local_types import kLocReal
from local_types import kLocArrInt
from local_types import kLocArrStr
from local_types import kLocArrReal

from native_types import kInt
from native_types import kStr
from native_types import kReal

# from abstract import KSP

from stack import Stack


class Local:
    _size = 32768
    _recursion_depth = 100
    _int_stack = Stack('local_vars_int', _size, int,
                       _recursion_depth)
    _str_stack = Stack('local_vars_str', _size, str,
                       _recursion_depth)
    _real_stack = Stack('local_vars_real', _size, float,
                        _recursion_depth)

    def __init__(self, idx):
        if not Local._int_stack:
            Local._int_stack = Stack('local_vars_int', Local._size,
                                     int, Local._recursion_depth)
        if not Local._str_stack:
            Local._str_stack = Stack('local_vars_str', Local._size,
                                     str, Local._recursion_depth)
        if not Local._real_stack:
            Local._real_stack = Stack('local_vars_real', Local._size,
                                      float, Local._recursion_depth)

        self.idx = idx
        self.int_stack = Local._int_stack
        self.str_stack = Local._str_stack
        self.real_stack = Local._real_stack

    def __call__(self, *args):
        variables = list()
        self.int_vars = list()
        self.str_vars = list()
        self.real_vars = list()
        for arg in args:
            stack, var = self.__get_obj_of_type(arg)
            if stack is self.int_stack:
                self.int_vars.append(var)
            if stack is self.str_stack:
                self.str_vars.append(var)
            if stack is self.real_stack:
                self.real_vars.append(var)
        if len(self.int_vars) > 0:
            self.int_vars = self.__push_and_get_vars(
                self.int_stack,
                self.int_vars)
            variables.extend(self.int_vars)

        if len(self.str_vars) > 0:
            self.str_vars = self.__push_and_get_vars(
                self.str_stack,
                self.str_vars)
            variables.extend(self.str_vars)

        if len(self.real_vars) > 0:
            self.real_vars = self.__push_and_get_vars(
                self.real_stack,
                self.real_vars)
            variables.extend(self.real_vars)
        return variables

    def __del__(self):
        if len(self.int_vars) > 0:
            self.int_stack.pop()
        if len(self.str_vars) > 0:
            self.str_stack.pop()
        if len(self.real_vars) > 0:
            self.real_stack.pop()

    def __get_obj_of_type(self, arg):
        availble = int, str, float, kInt, kStr, kReal
        if arg not in availble:
            if not isinstance(arg, list):
                raise TypeError('can be only one of: ' +
                                f'{availble}, {list}([type] * size)')

        name = 'name'
        if arg in (int, kInt):
            stack = self.int_stack
            var = kLocInt(name, 0)
        if arg in (str, kStr):
            stack = self.str_stack
            var = kLocStr(name, '')
        if arg in (float, kReal):
            stack = self.real_stack
            var = kLocReal(name, 0.0)

        if isinstance(arg, list):
            first = arg[0]
            if first not in availble:
                raise TypeError('list items can be only one of' +
                                f'{availble}')
            if first in (int, kInt):
                stack = self.int_stack
                var = kLocArrInt(name, length=len(arg))
            if first in (str, kStr):
                stack = self.str_stack
                var = kLocArrStr(name, length=len(arg))
            if first in (float, kReal):
                stack = self.real_stack
                var = kLocArrReal(name, length=len(arg))
        return stack, var

    def __push_and_get_vars(self,
                            stack,
                            in_vars):
        push_vars = dict()
        for idx, var in enumerate(in_vars):
            push_vars[f'{idx}'] = var
        stack.push(**push_vars)
        frame = stack.peek()
        out_vars = list()
        for var in push_vars:
            out_vars.append(frame[var])
        return out_vars


# from dev_tools import print_lines
# from dev_tools import unpack_lines
# from interfaces import IOutput

# # Local(int, list([int] * 1000000))
# KSP.toggle_test_state(True)
# # Local = LocalClass


# def Foo(arg):
#     IOutput.put(f'Foo{arg}')
#     if arg > 2:
#         return
#     loc = Local(arg)
#     x, y, z = loc(int, list([int] * 50), float)
#     x(1)
#     y[49] = 3
#     y[48] = 3
#     z(2.0)

#     pers = kInt(f'pers{arg}', 1)
#     pers(x())
#     IOutput.put(unpack_lines([f'Foo {arg} locals:',
#                               x(), y[49], y[47], z()]))
#     Foo(arg + 1)
#     IOutput.put(f'Foo{arg} end')


# Foo(1)
# # Foo(2)
# print_lines(IOutput.get())
