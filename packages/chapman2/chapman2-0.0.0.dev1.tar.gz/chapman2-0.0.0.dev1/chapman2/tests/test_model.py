import pickle
from unittest import TestCase, mock

from mongomock import MongoClient

import barin as b

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

    def test_new(self):
        msg = self.func.t.new()
        msgs = model.Message.m.find().all()
        self.assertEqual([msg], msgs)
        self.assertEqual(msg.task, 'test')
        self.assertEqual(msg.s.status, 'pending')
        self.assertEqual(
            dict(msg.payload),
            dict(
                args=pickle.dumps(()),
                kwargs=pickle.dumps({})))

    def test_n(self):
        msg = self.func.t.n()
        msgs = model.Message.m.find().all()
        self.assertEqual([msg], msgs)
        self.assertEqual(msg.task, 'test')
        self.assertEqual(msg.s.status, 'pending')
        self.assertEqual(
            dict(msg.payload),
            dict(
                args=pickle.dumps(()),
                kwargs=pickle.dumps({})))

    def test_spawn(self):
        msg = self.func.t.spawn()
        msgs = model.Message.m.find().all()
        self.assertEqual([msg], msgs)
        self.assertEqual(msg.task, 'test')
        self.assertEqual(msg.s.status, 'ready')
        self.assertEqual(
            dict(msg.payload),
            dict(
                args=pickle.dumps(()),
                kwargs=pickle.dumps({})))



