# Licensed with the 3-clause BSD license.  See LICENSE for details.

import os
import io
import uuid
import tarfile
from collections import defaultdict

import requests
from astropy.time import Time
from catch.model import Observation

from ...model import DataProducts
from ...services.catch_manager import Catch
from ...services.message import Message, TaskStatus

README = """
Downloaded from the Planetary Data System Small-Bodies Node's CATCH tool.

https://catch.astro.umd.edu/

Job ID: {}
Packaged: {} UTC

* archive-data/: Full-size images and PDS data labels (if available and/or
  requested).
* cutouts/: Image cutouts (if requested).
* sources.csv: List of files and source URLs.
* error.log: Error messages, if any.

"""


class PackageManager:
    """Handle file downloads and packaging.


    Examples
    --------

    """

    def __init__(self, job_id: uuid.UUID):
        self.job_id = job_id
        self.error_log: list[str] = []
        self.filenames: list[str] = []

    def package(self, catch: Catch, data_products: DataProducts) -> list[str]:
        self.get_observations(catch, data_products.observation_ids)
        manifest = self.get_manifest(data_products)
        self.download_and_package(manifest)
        return self.filenames

    def get_observations(self, catch: Catch, observation_ids: list[int]) -> None:
        """Get observation metadata by observation_id from the CATCH database."""

        self.observations = {
            obs.observation_id: obs
            for obs in (
                catch.db.session.query(Observation)
                .filter(Observation.observation_id.in_(observation_ids))
                .all()
            )
        }

        missing = set(observation_ids) - set(self.observations.keys())

        for m in missing:
            self.error_log.append(f"{m}: Not found in the CATCH database.")

    def get_manifest(self, data_products: DataProducts) -> dict[str, list]:
        """Forms lists of URLs from which to retrieve the data.


        Parameters
        ----------
        data_products : DataProducts
            The requested data products to download.  This may indicate, e.g.,
            if cutouts are to be downloaded.


        Returns
        -------
        manifest : dict
            List of URLs keyed by directory to which the data should be
            downloaded into.

        """

        manifest = defaultdict(set)

        for image in data_products.images:
            observation_id = image["observation_id"]
            obs = self.observations.get(observation_id)

            if obs is None:
                # missing observations should already be noted in the error log,
                # so continue on to the next one
                continue

            cutout_spec = image.get("cutout")
            if cutout_spec is None:
                url = obs.archive_url
                if url is None:
                    self.error_log.append(
                        f"{observation_id}: Full-size image not available for {obs.product_id}"
                    )
                    continue

                manifest["archive-data"].add(url)
            else:
                if not all([k in cutout_spec for k in ["ra", "dec", "size"]]):
                    self.error_log.append(
                        f"{observation_id}: Cannot get cutout for {obs.product_id}, cutouts require ra, dec, and size: {str(cutout_spec)}"
                    )
                    continue

                url = obs.cutout_url(**cutout_spec)
                if url is None:
                    self.error_log.append(
                        f"{observation_id}: Cannot get cutout for {obs.product_id}, cutouts not available for this data source."
                    )
                    continue

                manifest["cutouts"].add(url)

            if obs.label_url is not None:
                manifest["archive-data"].add(obs.label_url)

        # return as a plain dict with lists (not sets)
        return {k: list(v) for k, v in manifest.items()}

    def download_and_package(self, manifest: dict[str, list]):
        """Download the data from the URLs and package into gzipped tar files.

        Packge file names are appended onto ``self.filenames``.

        """

        msg = Message(self.job_id, status=TaskStatus.RUNNING, text="Fetching data.")

        t = Time.now().isot.replace(":", "").replace("-", "")
        root = f"catch-download-{t[:t.index('.')]}"
        filename = f"{root}.tar.gz"
        self.filenames.append(filename)

        tar = tarfile.open(filename, "w:gz")
        archive_contents = "file,url\n"

        total = sum([len(urls) for urls in manifest.values()])
        count = 0
        errors = 0

        def send_status_message():
            msg.text = (
                f"{count}/{total} files ({errors} error{'' if errors == 1 else 's'})"
            )
            msg.publish()

        for dir, urls in manifest.items():
            for url in urls:
                if count % 100 == 0:
                    send_status_message()

                count += 1

                response = requests.get(url)
                if response.status_code != 200:
                    self.error_log.append(
                        f"Could not download {url}: HTTP status code = {response.status_code}"
                    )
                    errors += 1
                    continue

                content = io.BytesIO(response.content)

                data_filename = os.path.basename(url)
                if "Content-Disposition" in response.headers:
                    # extract filename from Content-Disposition header
                    content_disposition = response.headers["Content-Disposition"]
                    data_filename = content_disposition.split("filename=")[1].strip(
                        '";'
                    )

                tar_info = tarfile.TarInfo(os.path.join(root, dir, data_filename))
                tar_info.size = len(content.getvalue())
                tar.addfile(tar_info, fileobj=content)

                archive_contents += ",".join((data_filename, url)) + "\n"

        send_status_message()

        # add readme, list of archive contents, and error log
        self.add_text_file(
            tar,
            README.format(self.job_id.hex, Time.now().iso),
            os.path.join(root, "README.txt"),
        )
        self.add_text_file(tar, archive_contents, os.path.join(root, "sources.csv"))
        self.add_text_file(
            tar, "\n".join(self.error_log), os.path.join(root, "error.log")
        )

        tar.close()

    @staticmethod
    def add_text_file(tar: tarfile.TarFile, text: str, filename: str):
        """Add a text file to the tar archive."""

        content = io.BytesIO()
        content.write(text.encode())
        content.seek(0)
        tar_info = tarfile.TarInfo(filename)
        tar_info.size = len(content.getvalue())
        tar.addfile(tar_info, fileobj=content)
        content.close()
