# Licensed with the 3-clause BSD license.  See LICENSE for details.

import os
import json
import urllib.parse
import uuid
from flask import request
from ..config import PackagingStatus, get_logger
from ..services.download import DataProducts, package
from ..services.message import (
    Message,
    get_message_stream_url,
    listen_for_task_messages,
    stop_listening_for_task_messages,
)


def package(body: dict) -> str:
    """Controller for packaging data."""

    logger = get_logger()
    job_id = uuid.uuid4()
    listen_for_task_messages(job_id)
    status = DataProducts(body["images"])

    packaging_status = package(job_id, status)

    Message.reset_t0()

    # setup the result object to send to the user
    result = {
        "job_id": job_id.hex,
        "queued": packaging_status == PackagingStatus.QUEUED,
        "queue_full": packaging_status == PackagingStatus.QUEUEFULL,
        "message": None,
        "message_stream": None,
        "results": None,
    }

    # form the results URL
    parsed: tuple = urllib.parse.urlsplit(request.url_root)
    results_url: str = urllib.parse.urlunsplit(
        (
            parsed[0],
            parsed[1],
            os.path.join(parsed[2], "download/data/", job_id.hex),
            "",
            "",
        )
    )

    # Set result properties (e.g., user message) based on queue status.
    if result["queued"]:
        result["message"] = (
            "Enqueued packaging request.  Listen to task messaging stream until job "
            "completed, then retrieve data from results URL."
        )
        result["message_stream"] = get_message_stream_url()
        result["results"] = results_url
    elif result["queue_full"]:
        result["message"] = "Queue is full, please try again later."
    else:
        result["message"] = (
            "Unexpected error.  Please report the issue if the problem persists."
        )

    # log this result
    logger.info(json.dumps(result))

    stop_listening_for_task_messages(job_id)

    return result
