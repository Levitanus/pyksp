import re

from interfaces import IOutput
from kspvar import KspVarObj


class KspCode:

    def __new__(cls, file, **kwargs):
        return KspCode.__call__(file, **kwargs)

    @staticmethod
    def __call__(file, **kwargs):

        with open(file, 'r') as f:
            lines = f.readlines()
        if kwargs:
            lines = KspCode.replace_vars(lines, kwargs)
        KspCode.append_code(lines)
        return

    @staticmethod
    def append_code(lines):
        for line in lines:
            IOutput.put(line)

    @staticmethod
    def replace_vars(lines, kwargs):
        newlines = list()
        for line in lines:
            for name, var in kwargs.items():
                line = KspCode.replace_var(line, name, var)
            newlines.append(line)
        return newlines

    @staticmethod
    def replace_var(line, name, var):
        if line.strip() == '':
            return line
        if isinstance(var, str):
            var = '"%s"' % var
        if isinstance(var, KspVarObj):
            var = var()

        name = str(name)
        return re.sub(r'\b' + name + r'\b', str(var), line)
