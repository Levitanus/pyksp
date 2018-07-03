import os
# import sys

import re

from ksp_compiler3 import ksp_builtins as bi
from abstract import KSP
# from abc import abstractmethod
from interfaces import IOutput

kw = bi.keywords


def get_callbacks():
    names = list()
    for item in kw:
        if re.match('on ', item):
            if not re.match('on ui_control', item):
                names.append(re.sub(r'on ', '', item))
    return names


callbacks_names = get_callbacks()


class Callbacks(KSP):

    instances = list()
    init_instance = None

    def __init__(self, name):
        self.code = list()
        self.name = name
        Callbacks.instances.append(self)

    def __call__(self, func):
        IOutput.set(self.code)
        func()
        IOutput.release()

    def refresh(self):
        self.code = list()

    @staticmethod
    def refresh_all():
        cb = Callbacks
        for instance in cb.instances:
            instance.refresh()
        if cb.init_instance is not None:
            cb.init_instance.refresh()

    @staticmethod
    def generate_code():
        cb = Callbacks
        code = list()
        for instance in cb.instances:
            instance_code = instance._generate_code()
            if len(instance_code) > 0:
                code.append('on %s' % instance.name)
                code.extend(instance_code)
                code.append('end on')
        return code

    def _generate_code(self):
        return self.code


class Init(Callbacks):

    def __init__(self):
        self.code = list()
        Callbacks.init_instance = self

    def generate_code(self):
        return self.code


def generate_callbacks(root):
    '''
    update interface for getting list of availeble
    callbacks from ksp_compiller3 and building python
    object inside callbacks_generated
    '''
    code = list()
    code.append('import callbacks as cb\n')
    for name in callbacks_names:
        string = '%s = cb.Callbacks("%s")\n' % (name, name)
        if name == 'init':
            string = '%s = cb.Init()\n' % name
        code.append(string)

    f = open(root + '/callbacks_generated.py', 'w')
    f.writelines(code)
    f.close()


if __name__ == '__main__':
    root = os.path.dirname(__file__)
    generate_callbacks(root)
