"""
/stream route namespace.
"""

from typing import Iterator, Union
import uuid

from flask import Response
from flask_restplus import Namespace, Resource, cors
from redis import Redis, StrictRedis
from redis.client import PubSub

from tasks import RQueues


API: Namespace = Namespace(name='Stream', path='/stream',
                           description='CATCH-APIs event stream')
strict_redis: Redis = StrictRedis()


@API.route("/<string:job_id>")
class StreamRoute(Resource):
    """Controller class for stream"""

    @API.doc('--event-stream--')
    @cors.crossdomain(origin='*')
    def get(self: 'StreamRoute', job_id: Union[str, uuid.UUID]) -> Response:
        '''CATCH-APIs event stream'''

        job_id = uuid.UUID(job_id, version=4)

        return Response(self.event_stream(job_id), mimetype="text/event-stream")

    @staticmethod
    def event_stream(job_id: uuid.UUID) -> Iterator[str]:
        """Inspect event stream."""

        pubsub: PubSub = strict_redis.pubsub()
        pubsub.subscribe()
        for message in pubsub.listen():
            print(message)
            if message['job_id'] != job_id.hex:
                continue

            msg: str
            if isinstance(message['data'], bytes):
                msg = message['data'].decode('utf-8')
            else:
                msg = message['data']
            yield f'data: {msg}\n\n'
