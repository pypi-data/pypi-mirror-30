import pickle

from . import errors
from . import model


class Task(object):
    _registry = {}

    def __init__(self, name):
        self._name = name
        self.register(name, self)

    def __repr__(self):
        return '<Task {}:{}>'.format(
            self._name,
            self.__class__.__name__)

    @classmethod
    def register(cls, name, task):
        cls._registry[name] = task

    @classmethod
    def lookup(cls, name):
        try:
            return cls._registry[name]
        except KeyError:
            raise errors.UnknownTaskError(name)

    @classmethod
    def reset(cls):
        cls._registry = {}

    def run(self, payload):
        raise NotImplementedError('run')


class FunctionTask(Task):
    _default_args = pickle.dumps(())
    _default_kwargs = pickle.dumps({})

    def __init__(self, name, function):
        super(FunctionTask, self).__init__(name)
        self._function = function

    def run(self, payload):
        args, kwargs = self._get_args(payload)
        self._function(*args, **kwargs)

    def n(self, *args, **kwargs):
        return self.new(args, kwargs)

    def new(self, args=(), kwargs=None, **options):
        if kwargs is None:
            kwargs = {}
        payload = dict(args=pickle.dumps(args), kwargs=pickle.dumps(kwargs))
        msg = model.Message.m.create(
            task=self._name,
            payload=payload,
            **options)
        msg.m.insert()
        return msg

    def spawn(self, *args, **kwargs):
        return self.new(args, kwargs, s={'status': 'ready'})

    def _make_payload(self, args, kwargs):
        payload = dict(args=pickle.dumps(args), kwargs=pickle.dumps(kwargs))
        return payload

    def _get_args(self, payload):
        args = payload.pop('args', self._default_args)
        kwargs = payload.pop('kwargs', self._default_kwargs)
        if payload:
            raise errors.InvalidPayload('Invalid args: {}'.format(list(payload)))
        return pickle.loads(args), pickle.loads(kwargs)
