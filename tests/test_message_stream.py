# Licensed with the 3-clause BSD license.  See LICENSE for details.

import json
import uuid
import pytest
from unittest import mock
from functools import partial
from starlette.testclient import TestClient
from catch_apis.services.message import Message
from catch_apis.services.stream import message_stream_service
from . import fixture_test_client, mock_messages


def test_message_stream_service(mock_messages):
    job_id = uuid.uuid4()
    Message(job_id, "this is a test message").publish()
    Message(job_id, "this is another test message").publish()

    messages = [message for message in message_stream_service(1)]

    # first two are our messages, the rest are stayin' alive and timeout
    data = json.loads(messages[0][6:])
    assert data["job_prefix"] == job_id.hex[:8]
    assert data["text"] == "this is a test message"

    data = json.loads(messages[1][6:])
    assert data["job_prefix"] == job_id.hex[:8]
    assert data["text"] == "this is another test message"


def test_stream(test_client: TestClient, mock_messages):
    job_id = uuid.uuid4()
    Message(job_id, "yet another test message").publish()
    Message(job_id, "test message, again").publish()
    with mock.patch(
        "catch_apis.services.stream.message_stream_service",
        partial(message_stream_service, 1),
    ):
        response = test_client.get("/stream")
        response.raise_for_status()
        text = response.content.decode()

    assert (
        'data: {"job_prefix": "'
        + job_id.hex[:8]
        + '", "text": "yet another test message", '
        in text
    )
    assert (
        'data: {"job_prefix": "' + job_id.hex[:8] + '", "text": "test message, again", '
        in text
    )
