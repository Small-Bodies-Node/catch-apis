# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
import requests

from starlette.testclient import TestClient

from catch_apis.services.catch_manager import catch_manager
import catch_apis.services.download
from catch_apis.services.download import DataProducts
import catch_apis.services.message
from catch_apis.services.message import Message
from catch_apis.tasks.download import package, PackageManager

from . import fixture_test_client, SkySurvey


class MockedJobsQueue:
    def __init__(self):
        pass

    def enqueue(*args, **kwargs):
        pass

    full = False


class MockedRedisConnection:
    def __init__(self):
        pass


class SkySurveyWithoutArchive(SkySurvey):
    archive_url = None
    label_url = None

    __mapper_args__ = {"polymorphic_identity": "test_sky_survey_without_archive"}

    def cutout_url(self, **kwargs):
        return None


class SkySurveyWithoutFullSize(SkySurvey):
    archive_url = None
    label_url = None

    __mapper_args__ = {"polymorphic_identity": "test_sky_survey_without_full_size"}

    def cutout_url(self, ra, dec, size=0.1, format="fits"):
        product_id = self.product_id[self.product_id.rindex(":") + 1 :]  # noqa: E203
        url = f"http://testserver/test/data/{product_id}.fits"

        if format == "jpeg":
            url = url[:-4]
        elif format != "fits":
            raise NotImplementedError
        return f"{url}?ra={ra}&dec={dec}&size={size}"


class SkySurveyWithoutCutouts(SkySurvey):
    __mapper_args__ = {"polymorphic_identity": "test_sky_survey_without_cutouts"}

    def cutout_url(self, **kwargs):
        return None


class TestPackageManager:
    def test_get_observations(self, test_client: TestClient):
        packager = PackageManager(uuid.uuid4())
        with catch_manager() as catch:
            packager.get_observations(catch, [0, 1, 2, 3])
            assert packager.error_log[0] == "0: Not found in the CATCH database."
            assert len(packager.observations) == 3
            assert set(packager.observations.keys()) == {1, 2, 3}

    def test_get_manifest(self):
        data_products = DataProducts(
            [
                {"observation_id": 0},
                {"observation_id": 0, "cutout": dict(ra=1, dec=2, size=3)},
                {"observation_id": 1},
                {"observation_id": 1, "cutout": dict(ra=1, dec=2, size=3)},
                {"observation_id": 2},
                {"observation_id": 2, "cutout": dict(ra=1, dec=2, size=3)},
                {"observation_id": 3},
                {"observation_id": 3, "cutout": dict(ra=1, dec=2, size=3)},
                {"observation_id": 3, "cutout": dict(ra=1, dec=2)},
                {"observation_id": 4},
            ],
            False,
        )

        packager = PackageManager(uuid.uuid4())
        packager.observations = {
            0: SkySurveyWithoutArchive(
                observation_id=0, product_id="urn:nasa:pds:gbo.ast.tss:data:0"
            ),
            1: SkySurveyWithoutFullSize(
                observation_id=1, product_id="urn:nasa:pds:gbo.ast.tss:data:1"
            ),
            2: SkySurveyWithoutCutouts(
                observation_id=2, product_id="urn:nasa:pds:gbo.ast.tss:data:2"
            ),
            3: SkySurvey(
                observation_id=3, product_id="urn:nasa:pds:gbo.ast.tss:data:3"
            ),
        }

        manifest = packager.get_manifest(data_products)
        assert sorted(manifest.get("archive-data")) == [
            "http://testserver/test/data/2.fits",
            "http://testserver/test/data/2.xml",
            "http://testserver/test/data/3.fits",
            "http://testserver/test/data/3.xml",
        ]
        assert sorted(manifest["cutouts"]) == sorted(
            [
                "http://testserver/test/data/1.fits?ra=1&dec=2&size=3",
                "http://testserver/test/data/3.fits?ra=1&dec=2&size=3",
            ]
        )


def test_download(test_client: TestClient, monkeypatch):
    # redirect requests to use the test client
    monkeypatch.setattr(requests, "get", test_client.get)

    # collect task messages instead of sending to redis
    messages = []

    def patched_publish(self):
        messages.append(self.text)

    monkeypatch.setattr(Message, "publish", patched_publish)

    images = [
        {"observation_id": 1},
        {"observation_id": 2},
        {"observation_id": 3},
    ]

    job_id = uuid.uuid4()
    data_products = DataProducts(images, previews=False)
    filenames = package(job_id, data_products)
    assert len(filenames) == 1
    assert filenames[0].startswith("catch-download-")
    assert len(filenames[0]) == 37

    assert messages == [
        "Packaging started",
        "0/6 files (0 errors)",
        "6/6 files (0 errors)",
        "Packaging complete",
    ]


def test_download_api(test_client: TestClient, monkeypatch):
    # redirect requests to use the test client
    monkeypatch.setattr(requests, "get", test_client.get)

    # don't send messages or queue jobs to redis
    def patched_publish(self):
        pass

    monkeypatch.setattr(Message, "publish", patched_publish)

    monkeypatch.setattr(catch_apis.services.download, "JobsQueue", MockedJobsQueue)
    monkeypatch.setattr(
        catch_apis.services.message, "listen_for_task_messages", lambda job_id: None
    )
    monkeypatch.setattr(
        catch_apis.services.message,
        "stop_listening_for_task_messages",
        lambda job_id: None,
    )

    # test for queued request
    data = {
        "images": [
            {"observation_id": 1},
            {"observation_id": 2},
            {"observation_id": 3},
        ],
        "previews": False,
    }

    response = test_client.post("/package", json=data)
    response.raise_for_status()
    result = response.json()

    uuid.UUID(result["job_id"], version=4)

    assert result["queued"]
    assert not result["queue_full"]
    assert result["results"] == f"http://testserver/download/{result['job_id']}"

    # test queue full
    MockedJobsQueue.full = True
    response = test_client.post("/package", json=data)
    response.raise_for_status()
    result = response.json()

    assert not result["queued"]
    assert result["queue_full"]
    assert result["results"] is None

    def error(self):
        raise RuntimeError

    with monkeypatch.context() as m:
        m.setattr(MockedJobsQueue, "__init__", error)
        response = test_client.post("/package", json=data)
        response.raise_for_status()
        result = response.json()
        assert (
            result["message"]
            == "Unexpected error.  Please report the issue if the problem persists."
        )
