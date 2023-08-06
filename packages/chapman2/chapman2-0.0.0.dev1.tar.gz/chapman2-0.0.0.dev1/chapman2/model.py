from datetime import datetime
import logging

import bson
from pymongo import ReturnDocument

import barin as b
import barin.schema as s

log = logging.getLogger(__name__)
metadata = b.Metadata()

# Message statuses: pending, ready, busy, error

_schedule = b.subdocument(
    metadata, '_schedule',
    b.Field('priority', int, default=10),
    b.Field('after', datetime, default=datetime.fromtimestamp(0)),
    b.Field('status', str, default='pending'),
    b.Field('message', str, default=''),
    b.Field('worker', str, default=None))


@b.cmap(b.collection(
    metadata, 'c2.message',
    b.Field('_id', s.ObjectId, default=bson.ObjectId),
    b.Field('s', metadata.cref('_schedule')),
    b.Field('task', str),
    b.Field('payload', {str: None})))
class Message(object):

    def __repr__(self):
        return '<Message {}: {}>'.format(self._id, self.task)

    @classmethod
    def reserve(cls, worker):
        now = datetime.utcnow()
        q = cls.m.query
        q = q.match(cls.s.status == 'ready')
        q = q.match(cls.s.after <= now)
        q = q.sort(-cls.s.priority)
        q = q.sort(-cls.s.priority)
        return q.find_one_and_update(
            cls.s.status.set('busy')
            & cls.s.worker.set(worker),
            return_document=ReturnDocument.AFTER)

    def error(self, message):
        cls = self.__class__
        self.m.update(
            cls.s.status.set('error') &
            cls.s.message.set(message))