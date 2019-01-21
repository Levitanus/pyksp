import unittest as ut
import typing as ty

if __name__ == '__main__':
    __name__ = 'pyksp.tests.test_abstract'

from .. import abstract as ab
from textwrap import dedent


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
        self.WithInit()
        self.WithoutInit()
        self.assertEqual(self.WithInit.generate_inits(),
                         ['init of test_object'])


class TestNames(ut.TestCase):
    def tearDown(self) -> None:
        ab.NameVar.refresh()

    def test_base(self) -> None:
        name = ab.NameBase('name')
        self.assertEqual(name(), 'name')
        self.assertEqual(name.name, 'name')
        self.assertEqual(name.prefix, '')
        self.assertEqual(name.postfix, '')
        name.prefix = 'prefix'
        name.postfix = 'postfix'
        self.assertEqual(name.prefix, 'prefix')
        self.assertEqual(name.postfix, 'postfix')
        self.assertEqual(name(), 'prefixnamepostfix')

    def test_var(self) -> None:
        namevar = ab.NameVar('var', '$', '[15]')
        self.assertEqual(namevar(), '$var[15]')
        with self.assertRaises(NameError):
            ab.NameVar('var')
        ab.NameVar.refresh()
        self.assertTrue(ab.NameVar('var'))

    def test_compacted_var(self) -> None:
        ab.NameVar('var')
        ab.KSP.compacted_names = True
        with self.assertRaises(NameError):
            ab.NameVar('var')
        ab.NameVar.refresh()
        compacted = ab.NameVar('var')
        with self.assertRaises(NameError):
            ab.NameVar('var')
        self.assertEqual(compacted(), 'fuhgd')
        self.assertEqual(compacted.full, 'var')
        preserved = ab.NameVar('preserved', preserve=True)
        self.assertEqual(preserved(), 'preserved')
        ab.KSP.compacted_names = False
        ab.NameVar.refresh()

    def test_scope(self) -> None:
        ab.NameVar('var')
        ab.NameVar.scope('scoped')
        scoped = ab.NameVar('var')
        self.assertEqual(scoped(), 'scoped_var')
        ab.NameVar.scope('to_levels')
        scoped2 = ab.NameVar('var')
        self.assertEqual(scoped2(), 'to_levels_var')
        ab.NameVar.scope()
        with self.assertRaises(NameError):
            ab.NameVar('var')
        ab.NameVar.scope()
        unscoped = ab.NameVar('unscoped')
        self.assertEqual(unscoped(), 'unscoped')


class TestLittle(ut.TestCase):

    def test_AstNull(self) -> None:
        a = ab.AstNull()
        self.assertIsInstance(a, ab.AstRoot)
        with self.assertRaises(ab.AstRoot.NullError):
            a.expand()
        with self.assertRaises(ab.AstRoot.NullError):
            a.get_value()

    def test_AstString(self) -> None:
        s = ab.AstString('mystring')
        with self.assertRaises(TypeError):
            ab.AstString(2)
        self.assertIsInstance(s, ab.AstRoot)
        with self.assertRaises(ab.AstRoot.NullError):
            s.get_value()
        self.assertEqual(s.expand(), 'mystring')

    def test_AstRoot(self) -> None:
        with self.assertRaises(TypeError):
            ab.AstRoot()

        class Concrete(ab.AstRoot):
            def expand(self) -> str:
                return 'expanded'

            def get_value(self) -> None:
                return
        c = Concrete()
        with self.assertRaises(AttributeError):
            c.queue_line
        with self.assertRaises(TypeError):
            c.queue_line = 'True'
        c.queue_line = 2
        self.assertEqual(c.queue_line, 2)
        self.assertEqual(c.expand(), 'expanded')
        self.assertTrue(c.expanded)

    def test_OutputBlock(self) -> None:
        ifb = ab.OutputBlock('if', 'end if')
        self.assertEqual(ifb, ab.OutputBlock('if', 'end if'))
        self.assertNotEqual(ifb, ab.OutputBlock('if', 'if'))
        self.assertNotEqual(ifb, 1)
        self.assertEqual(ifb.open.expand(), 'if')
        self.assertEqual(ifb.open_str, 'if')
        self.assertEqual(ifb.close.expand(), 'end if')
        self.assertEqual(ifb.close_str, 'end if')

        with self.assertRaises(TypeError):
            ab.OutputBlock(1, '1')
        with self.assertRaises(TypeError):
            ab.OutputBlock('1', 1)


class TestOutput(ut.TestCase):

    def setUp(self) -> None:
        self.ast = ab.AstString('line')

    def test_put(self) -> None:
        with self.assertRaises(TypeError):
            ab.Output(-1)
        with self.assertRaises(TypeError):
            ab.Output(1.1)

        out = ab.Output(0)
        with self.assertRaises(TypeError):
            out.put_immediatly('ads')
        out.put_immediatly(self.ast)
        ret = out.get()
        self.assertIsInstance(ret, ab.OutputGot)
        self.assertEqual(ret[-1].line, 'line')

    def test_blocks(self) -> None:
        self.maxDiff = None
        out = ab.Output(0)
        with self.assertRaises(RuntimeError):
            out.close_block(ab.OutputBlock('if', 'end if'))
        out.open_block(ab.OutputBlock('on init', 'end on'))
        out.put_immediatly(self.ast)
        out.open_block(ab.OutputBlock('if', 'end if'))
        out.put_immediatly(self.ast)
        out.wait_for_block(ab.OutputBlock('if', 'end if'),
                           ab.OutputBlock('else', 'end if'))
        with self.assertRaises(RuntimeError):
            out.open_block(ab.OutputBlock('if', 'end if'))
        out.put_immediatly(self.ast)
        out.open_block(ab.OutputBlock('if', 'end if'))
        out.put_immediatly(self.ast)
        out.wait_for_block(ab.OutputBlock('if', 'end if'),
                           ab.OutputBlock('else', 'end if'))
        out.open_block(ab.OutputBlock('else', 'end if'))
        out.put_immediatly(self.ast)
        out.put_to_queue(ab.AstString('queued_line'))
        out.put_to_queue(self.ast)
        out.open_block(ab.OutputBlock('if', 'end if'))
        with self.assertRaises(RuntimeError):
            out.close_block(ab.OutputBlock('else', 'end if'))
        out.put_immediatly(self.ast)
        out.close_block(ab.OutputBlock('if', 'end if'))
        out.close_block(ab.OutputBlock('else', 'end if'))

        out.close_block(ab.OutputBlock('on init', 'end on'))
        out_str = dedent('''
            on init
                line
                if
                    line
                end if
                line
                if
                    line
                else
                    line
                    queued_line
                    if
                        line
                    end if
                end if
            end on''')[1:]
        self.assertEqual(out.get_str(), out_str)
        got = out.get()
        newOut = ab.Output(0)
        newOut.put_lines(got)
        self.assertEqual(newOut.get_str(), out_str)

    def test_blocking(self) -> None:
        out = ab.Output(0)
        block = ab.OutputBlock('open', 'close')
        with self.assertRaises(RuntimeError):
            out.release()
        out.block()
        out.put_immediatly(self.ast)
        out.put_to_queue(self.ast)
        with self.assertRaises(RuntimeError):
            out.block()
        out.open_block(block)
        out.wait_for_block(block, ab.OutputBlock('new', 'end new'))
        out.close_block(block)
        out.release()
        out.put_immediatly(self.ast)
        self.assertEqual(out.get_str(), 'line')


class TestKSP(ut.TestCase):

    def tearDown(self) -> None:
        ab.KSP.refresh()

    class Child(ab.KSP):
        pass

    def test_output(self) -> None:
        with self.assertRaises(RuntimeError):
            ab.KSP.get_out()
        out = ab.KSP.new_out()
        self.assertIsInstance(out, ab.Output)
        self.assertIs(out, ab.KSP.get_out())
        out1 = ab.KSP.new_out()
        out1.put_immediatly(ab.AstString('line'))
        self.assertEqual(out1.get(), ab.KSP.pop_out())

        out1 = ab.KSP.new_out()
        out1.put_immediatly(ab.AstString('line'))
        ab.KSP.merge_out()
        self.assertEqual(out.get_str(), 'line')

    def test_childs(self) -> None:
        root = ab.KSP
        child = self.Child()
        self.assertFalse(child.is_compiled())
        root.set_compiled(True)
        self.assertTrue(child.is_compiled())
        self.assertFalse(child.is_bool())
        root.set_bool(True)
        self.assertTrue(child.is_bool())
        with self.assertRaises(TypeError):
            root.set_bool(1)

    def test_listener(self) -> None:
        class Error(Exception):
            pass

        def func(event: ab.ListenerEventType) -> None:
            raise Error(event)

        class Event(ab.ListenerEventBase):
            pass
        event = Event()
        self.assertIsNone(ab.KSP.event(event))
        listener = ab.EventListener()
        ab.KSP.set_listener(listener)
        listener.bind_to_event(func, Event)
        with self.assertRaises(Error) as e:
            ab.KSP.event(event)
        self.assertEqual(str(e.exception), str(event))
