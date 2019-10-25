"""
Controller for image cutout service.
"""

import logging
import uuid
from typing import Dict, Union

import flask_restplus as FRP
from flask import request, Response, jsonify
from redis import Redis
from rq import Queue

from env import ENV
from models.images import App
import services.images as service
from tasks import RQueues
from tasks.images import neat_cutout

API: FRP.Namespace = App.api

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/neat")
class NeatCutouts(FRP.Resource):
    """Controller for NEAT cutouts."""

    @API.doc('--images/neat--')
    @API.param(
        'productid', _in='query',
        description='NEAT survey product ID from PDS archive.  Required.'
    )
    @API.param(
        'ra', _in='query',
        description='Cutout Right Ascension (float, deg).'
    )
    @API.param(
        'dec', _in='query',
        description='Cutout Declination (float, deg).'
    )
    @API.param(
        'size', _in='query',
        description='Cutout size (integer, arcmin).  Optional.  Default 5.'
    )
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'NeatCutouts') -> Response:
        """NEAT survey image cutout service."""

        # Extract params from URL
        query: Dict[str, Union[str, int, float, None]] = {
            'productid': request.args.get('productid', '', str),
            'ra': request.args.get('ra', None, float),
            'dec': request.args.get('dec', None, float),
            'size': request.args.get('size', 5, int)
        }

        # Connect to started-jobs queue
        conn = Redis.from_url('redis://')
        queue = Queue(RQueues.START_JOBS, connection=conn)
        total_jobs = len(queue.jobs)

        # Build immediate response
        response: Response
        if total_jobs > 100:
            response = jsonify({
                "message": "Error: queue is full."
            })
            response.status_code = 200
        else:
            # unique job ID
            job_id: uuid.UUID = uuid.uuid4()

            url = service.build_url(query['productid'], ra=query['ra'],
                                    dec=query['dec'], size=query['size'])

            message: str
            if url.startswith(ENV.CATCH_FULLFRAME_BASE_URL):
                message = 'Full-frame image.'
            else:
                message = 'Generating cutout.'

                # Spin out task to worker, return job_id
                queue.enqueue(neat_cutout, query['productid'], job_id,
                              query['ra'], query['dec'], size=query['size'],
                              job_id=job_id.hex)

            response = jsonify({
                "message": message,
                "query": query,
                "url": url,
                "job_id": job_id.hex
            })
            response.status_code = 200

        return response
