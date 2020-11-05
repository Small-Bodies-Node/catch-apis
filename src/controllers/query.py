"""
Controller for survey searches.
"""

import uuid
from typing import Dict, Union, Any, List

import flask_restplus as FRP
from flask import request
from redis import Redis, StrictRedis
from rq import Queue

from models.query import App
import services.query as service
from services.name_search import name_search
from tasks import RQueues
from tasks.message import Message
from tasks.query import catch_moving_target, cutout_moving_targets
from util import jsonify_output
from env import ENV

API: FRP.Namespace = App.api

strict_redis: Redis = StrictRedis()


@API.route("/moving")
class Query(FRP.Resource):
    """Controller class for CATCH queries of moving targets."""

    @API.doc('--query/moving--')
    @API.param(
        'target', _in='query',
        description='Search for this moving target.'
    )
    @API.param(
        'source', _in='query',
        description='Search this observation source or "any".'
    )
    @API.param(
        'cached', _in='query',
        description='Return cached results, if available.'
    )
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(App.query_model)
    def get(self: 'Query') -> Dict[
            str, Union[str, bool, Dict[str, Union[str, bool]]]]:
        """Query for moving target."""
        from . import URL_PREFIX    # avoid circular dependency

        # Extract params from URL
        query: Dict[str, Union[str, bool]] = {
            'target': request.args.get('target', '', str),
            'source': request.args.get('source', 'any', str),
            'cached': request.args.get('cached', True, FRP.inputs.boolean)
        }

        # Test target name, if valid, proceed
        target_type: str
        target_type = service.parse_target_name(query['target'])[0]

        # Connect to jobs queue
        conn = Redis.from_url('redis://')
        queue = Queue(RQueues.JOBS, connection=conn)
        total_jobs = len(queue.jobs)

        # Build immediate response
        response: Dict[str, Union[str, bool, Dict[str, Union[str, bool]]]]
        if target_type == 'unknown':
            response = {
                "message": "Invalid target name.",
                "query": query,
                "queued": False
            }
        elif ENV.REDIS_MAX_QUEUE_SIZE > 0 and total_jobs > ENV.REDIS_MAX_QUEUE_SIZE:
            response = {
                "message": "Error: queue is full.",
                "queued": False,
                "isQueueFull": True
            }
        else:
            # unique job ID
            job_id: uuid.UUID = uuid.uuid4()

            results_url: str = '{}/{}/caught/{}'.format(
                request.url_root.strip('/'), URL_PREFIX.strip('/'),
                job_id.hex)

            response = {
                "message": "",
                "queued": True,
                "isQueueFull": False,
                "query": query,
                "job_id": job_id.hex,
                "results": results_url
            }

            cached = False
            if query['cached']:
                # check Catch Queries cache for previous search results
                cached = service.check_cache(
                    query['target'], query['source'], save_to=job_id)

            # message for task messaging stream
            msg: Message = Message(job_id)
            msg.status = 'queued'
            msg.text = 'Job queue number {}'.format(total_jobs + 1)
            strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))

            if cached:
                # Make sure cutouts are avilable.  Spin out task to worker.
                queue.enqueue(cutout_moving_targets, job_id)

                response['message'] = (
                    'Found cached data.  Retrieve from results URL.'
                )
                response['queued'] = False  # query is not queued
            else:
                # Spin out actual search to worker
                queue.enqueue(catch_moving_target, query['target'],
                              query['source'], query['cached'], job_id)

                response['message'] = (
                    'Enqueued search.  Listen to task messaging stream until'
                    ' job completed, then retrieve data from results URL.'
                )
                response['queued'] = True  # query is queued

        return response


@API.route("/name-old")
class QueryName(FRP.Resource):
    """Controller class for testing target names."""

    @API.doc('--query/name--')
    @API.param(
        'name', _in='query',
        description='Target name to test.'
    )
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(App.target_name_model)
    def get(self: 'QueryName') -> Dict[str, Union[bool, str]]:
        """Query moving target name."""

        # Extract parameter from URL
        name: str = request.args.get('name', '', str)
        target_type: str
        match: str
        target_type, match = service.parse_target_name(name)
        valid: bool = target_type != 'unknown'

        response: Dict[str, Union[str, Union[bool, str]]] = {
            'name': name,
            'type': target_type,
            'match': match,
            'valid': valid
        }
        return response
