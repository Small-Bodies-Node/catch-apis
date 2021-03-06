
"""
Demo Routes Module
Just a bunch of simple routes that you can reference/copy to start developing new routes
"""

import time
import logging
import typing
import uuid

from flask import jsonify, request, Response
import flask.wrappers as FLW
import flask_restplus as FRP

from redis import Redis, StrictRedis
from rq import Queue
from tasks import RQueues

strict_redis: Redis = StrictRedis()


API = FRP.Namespace(
    name='Demo',
    path="/demo",
    description='Root route; used for demo-ing the API is up and running, etc.'
)

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/")
class DemoRoutes(FRP.Resource):
    """Controller class for demo-routes"""

    @API.doc('--demo--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'DemoRoutes') -> typing.Any:
        '''Returns trivial json object'''

        # Return a trivial json
        res: FLW.Response = jsonify(
            {
                "message": "This is the demo GET route which doesn't do much."
            }
        )
        res.status_code = 200
        return res

    @API.doc('--demo--')
    @API.param('example', description='Place a string here as an example of a POST request', _in='body')
    @FRP.cors.crossdomain(origin='*')
    def post(self: 'DemoRoutes') -> FLW.Response:
        """Returns trivial json object"""

        # Demo logging
        logger.debug('"DEMO POST DEBUG"')
        logger.info('"DEMO POST INFO"')
        logger.warning('"DEMO POST WARNING"')
        logger.critical('"DEMO POST CRITICAL"')

        # Extract data from POST body
        data = request.json

        # Return posted data as part of simple POST-cycle demo
        res: FLW.Response = jsonify(
            {
                "message":
                """
                    Wow! This is the data you posted!
                """,
                "posted-data": data
            }
        )
        res.status_code = 200
        return res


@API.route("/staged")
class StagedDemoRoutes(FRP.Resource):
    """Controller class for staged-demo-routes"""

    @API.doc('--staged-demo--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'StagedDemoRoutes') -> typing.Any:
        '''Returns trivial json object'''

        # Return a trivial json
        res: FLW.Response = jsonify(
            {
                "message": "This is the STAGED demo GET route which doesn't do much."
            }
        )
        res.status_code = 200
        return res


@API.route("/redis/")
class DemoRedisRoutes(FRP.Resource):
    """Controller class for demo-redis-routes"""

    @API.doc('--demo-redis--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'DemoRedisRoutes') -> typing.Any:
        '''Returns json object with uuid for job spun out to worker'''

        # Connect to jobs queue
        conn = Redis.from_url('redis://')
        queue = Queue(RQueues.JOBS, connection=conn)
        total_jobs = len(queue.jobs)

        # Build immediate response
        res: FLW.Response
        if total_jobs > 20:
            res = jsonify(
                {
                    "message": "There are too many jobs in this queue!!!"
                }
            )
            res.status_code = 200
            return res
        else:
            # Create uuid for job, spin out task to worker, return uuid
            job_uuid: uuid.UUID = uuid.uuid4()
            job = queue.enqueue(example_task, 15, job_uuid)
            res = jsonify(
                {
                    "message": "This is the demo GET route which doesn't do much.",
                    "job_uuid": job_uuid.hex
                }
            )
            res.status_code = 200
            return res


@API.route("/stream/")
class DemoStreamRoutes(FRP.Resource):
    """Controller class for stream"""

    @API.doc('--demo-stream--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'DemoStreamRoutes') -> typing.Any:
        '''Returns streamed stuff'''
        print('??????')
        return Response(event_stream(),
                        mimetype="text/event-stream")


def event_stream() -> typing.Any:
    """ Stream generator function piping data to clients subscribed via SSE API """
    pubsub = strict_redis.pubsub()
    pubsub.subscribe(RQueues.TASK_MESSAGES)
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        print(message)
        msg = message['data']
        if type(msg) is bytes:
            msg = msg.decode('utf-8')
        yield 'data: %s\n\n' % msg


def example_task(seconds: int, job_uuid: uuid.UUID) -> None:
    """Simple demo of long-running task to be handled by async worker.

    As work is done, post the API-formatted message as JSON string to
    redis queue, which will be piped to client's SSE API

    """

    from tasks.message import Message

    msg: Message = Message(job_uuid)
    print('Starting task')
    msg.status = 'running'
    for i in range(seconds):
        print(i)
        msg.text = str(i)
        strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))
        time.sleep(1)
    print('Task completed: '+job_uuid.hex)
    msg.status = 'success'
    msg.text = str(seconds)
    strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))
