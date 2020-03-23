"""
/stream route namespace.
"""

from typing import Iterator
import uuid

from flask import Response
from flask_restplus import Namespace, Resource, cors
from redis import Redis, StrictRedis
from redis.client import PubSub

from tasks import RQueues


API: Namespace = Namespace(name='Stream', path='/stream',
                           description='CATCH-APIs event stream')
strict_redis: Redis = StrictRedis()


@API.route("/")
class StreamRoute(Resource):
    """Controller class for stream"""

    @API.doc('--event-stream--')
    @cors.crossdomain(origin='*')
    def get(self: 'StreamRoute') -> Response:
        '''CATCH-APIs event stream'''

        return Response(
            self.event_stream(),
            mimetype="text/event-stream",
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Keep-Alive': 'timeout=55'
            }
        )

    @staticmethod
    def event_stream() -> Iterator[str]:
        """Inspect event stream."""

        pubsub: PubSub = strict_redis.pubsub()
        pubsub.subscribe(RQueues.FINISH_JOBS)
        for message in pubsub.listen():
            print(message)
            msg: str
            if isinstance(message['data'], bytes):
                msg = message['data'].decode('utf-8')
            else:
                msg = message['data']
            yield f'data: {msg}\n\n'
