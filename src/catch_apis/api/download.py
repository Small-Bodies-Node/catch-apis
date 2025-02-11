# Licensed with the 3-clause BSD license.  See LICENSE for details.

import os
import json
import urllib.parse
import uuid
from flask import request
from ..config import PackagingStatus, get_logger
from ..services import download
from ..services.message import (
    Message,
    get_message_stream_url,
    listen_for_task_messages,
    stop_listening_for_task_messages,
)


def package(body: dict) -> dict:
    """Controller for packaging data."""

    logger = get_logger()
    job_id = uuid.uuid4()
    listen_for_task_messages(job_id)
    Message.reset_t0()

    # setup the result object to send to the user
    result = {
        "job_id": job_id.hex,
        "queued": False,
        "queue_full": False,
        "message": None,
        "message_stream": None,
        "results": None,
    }

    # enqueue the package task
    try:
        data_products = download.DataProducts(**body)
        packaging_status = download.package(job_id, data_products)
        result["queued"] = packaging_status == PackagingStatus.QUEUED
        result["queue_full"] = packaging_status == PackagingStatus.QUEUEFULL
    except:
        logger.exception("Unexpected error.")

    # form the results URL
    parsed = urllib.parse.urlsplit(request.url_root)
    results_url = urllib.parse.urlunsplit(
        (
            parsed[0],
            parsed[1],
            os.path.join(parsed[2], "download/", job_id.hex),
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
