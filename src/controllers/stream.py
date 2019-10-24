"""
/stream route namespace.
"""

from typing import Iterator

from flask import Response
from flask_restplus import Namespace, Resource, cors
from redis import Redis, StrictRedis
from redis.client import PubSub

from tasks import RQueues


API: Namespace = Namespace(name='Stream', path='/stream',
                           description='CATCH-APIs event stream')
strict_redis: Redis = StrictRedis()


@API.route("")
class StreamRoute(Resource):
    """Controller class for stream"""

    @API.doc('--demo-stream--')
    @cors.crossdomain(origin='*')
    def get(self: 'StreamRoute') -> Response:
        '''CATCH-APIs event stream'''

        return Response(self.event_stream(), mimetype="text/event-stream")

    @staticmethod
    def event_stream() -> Iterator[str]:
        pubsub: PubSub = strict_redis.pubsub()
        pubsub.subscribe(RQueues.FINISH_JOBS)
        for message in pubsub.listen():
            print(message)
            msg = message['data']
            if type(msg) is bytes:
                msg = msg.decode('utf-8')
            yield f'data: {msg}\n\n'
