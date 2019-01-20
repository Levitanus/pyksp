import unittest as ut
import typing as ty

if __name__ == '__main__':
    __name__ = 'pyksp.tests.test_abstract'

from .. import new_abstract as ab


class TestEventListener(ut.TestCase):

    def setUp(self) -> None:
        self.listener = ab.EventListener()
        self.out: ty.List[str] = list()

    class TestEvent(ab.ListenerEventBase):
        """docstring for TestEvent"""

        def __init__(self, arg: int) -> None:
            self.arg = arg

    def runTest(self) -> None:
        def get_arg(event: TestEventListener.TestEvent) -> None:
            self.out.append(str(event.arg))

        self.listener.bind_to_event(get_arg,
                                    self.TestEvent)
        self.listener.put_event(self.TestEvent(4))
        self.assertEqual(self.out[-1], '4')


class TestKspObject(ut.TestCase):

    class WithoutInit(ab.KspObject):
        def __init__(self, name: str='test_object', *,
                     has_init: bool=False) -> None:
            super().__init__(ab.NameBase(name), has_init=has_init)

        def generate_init(self) -> ty.List[str]:
            return [f'init of {self.name()}']

    class WithInit(WithoutInit, ab.HasInit):
        def __init__(self, name: str='test_object') -> None:
            super().__init__(name, has_init=True)

    def runTest(self) -> None:
        with_init = self.WithInit()
        without_init = self.WithoutInit()
        self.assertEqual(self.WithInit.generate_inits(),
                         ['init of test_object'])
