# Licensed with the 3-clause BSD license.  See LICENSE for details.

import os
import uuid
import requests
from starlette.testclient import TestClient
from catch_apis.services.download import DataProducts
from catch_apis.services.message import Message
from catch_apis.tasks.download import package, PackageManager
from catch_apis.services.catch_manager import catch_manager
from . import fixture_test_client


class TestPackageManager:
    def test_get_observations(self, test_client: TestClient):
        packager = PackageManager("1")
        with catch_manager() as catch:
            packager.get_observations(catch, [0, 1, 2, 3])
            assert packager.error_log[0] == "0: Not found in the CATCH database."
            assert len(packager.observations) == 3
            assert [obs.observation_id for obs in packager.observations] == [1, 2, 3]


def test_download(test_client: TestClient, monkeypatch):
    monkeypatch.setattr(requests, "get", test_client.get)

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


def test_download_api(test_client: TestClient):
    data = {
        "images": [
            {"observation_id": 1},
            {"observation_id": 2},
            {"observation_id": 3},
        ]
    }

    response = test_client.post("/download/package", data=data)
    response.raise_for_status()

    assert response.content == "ca850ab24f6f1ca49c401d66199673e2.tar.gz"
