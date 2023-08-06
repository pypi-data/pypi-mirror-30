from unittest import TestCase, mock

from mongomock import MongoClient

from chapman2 import task, Task
from chapman2 import model


class TestFunctionTasks(TestCase):

    def setUp(self):
        self.cli = MongoClient()
        self.db = self.cli.test
        model.metadata.bind(self.db)

        @task('test')
        def func():
            pass

        self.func = func

    def tearDown(self):
        Task.reset()

    def test_reserve(self):
        self.func.t.spawn()
        reserved = model.Message.reserve('test-worker')
        msgs = model.Message.m.find().all()
        self.assertEqual(msgs, [reserved])
        self.assertEqual(reserved.s.worker, 'test-worker')
        self.assertEqual(reserved.s.status, 'busy')

    def test_call(self):
        test2 = mock.Mock('test2')
        task('test2')(test2)
        test2.t.run({})
        test2.assert_called_with()

    def test_run_message(self):
        test2 = mock.Mock('test2')
        task('test2')(test2)
        m = test2.t.spawn()
        test2.t.run(m.payload)
        test2.assert_called_with()

    def test_run_message_args(self):
        test2 = mock.Mock('test2')
        task('test2')(test2)
        m = test2.t.spawn(1, 2, a=3)
        test2.t.run(m.payload)
        test2.assert_called_with(1, 2, a=3)