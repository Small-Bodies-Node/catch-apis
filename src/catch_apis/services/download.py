import os
import io
import tarfile
from hashlib import md5
from astropy.table import Table
from catch.model import Observation
from .catch_manager import Catch, catch_manager
import requests


def package(images: list[dict]) -> dict:
    """Package data and return filename.


    Parameters
    ----------
    images : list of dict
        Image specifications:
            - observation_id: (required)
            - cutout: (optional)
              - ra: right ascension, degrees
              - dec: declination, degrees
              - size: cutout size, degrees
              - format: cutout format


    Returns
    -------
    results : dict

    """

    observation_ids: list[int] = [image["observation_id"] for image in images]

    observations, error_log = _get_observations(observation_ids)

    result = _get_urls(images, observations)
    manifest = result[0]
    error_log.extend(result[1])

    filename: str = md5(str(images).encode()).hexdigest() + ".tar.gz"
    _download_and_package(manifest, error_log, filename)

    return filename


def _get_observations(
    observation_ids: list[int],
) -> tuple[list[Observation], list[str]]:
    catch: Catch
    observations: list[Observation]
    with catch_manager() as catch:
        observations = (
            catch.db.session.query(Observation)
            .filter(Observation.observation_id.in_(observation_ids))
            .all()
        )
        catch.db.session.expunge_all()

    missing: set[int] = set(observation_ids) - {
        obs.observation_id for obs in observations
    }

    error_log: list[str] = []
    for m in missing:
        error_log.append(f"{m}: Not found in the CATCH database.")

    return observations, error_log


def _get_urls(
    images: list[dict], observations: list[Observation]
) -> tuple[list[dict], list[str]]:
    images_by_id: dict[int, dict] = {image["observation_id"] for image in images}

    manifest: list[dict] = []
    error_log: list[str] = []
    for obs in observations:
        url: str | None
        cutout_spec = images_by_id[obs.observation_id].get("cutout")
        if cutout_spec is None:
            url = obs.archive_url()
            if url is None:
                error_log.append(
                    f"{obs.observation_id}: Full-size image not available for {obs.product_id}"
                )
            manifest["archive-data"].append(url)
        else:
            if not all([k in cutout_spec for k in ["ra", "dec", "size"]]):
                error_log.append(
                    f"{obs.observation_id}: Cannot get cutout for {obs.product_id}, cutouts require ra, dec, and size: {str(cutout_spec)}"
                )
                continue
            manifest["cutouts"].append(obs.cutout_url(**cutout_spec))

        url = obs.label_url()
        if url is not None:
            manifest["archive-data"].append(url)

    return manifest, error_log


def _download_and_package(
    manifest: list[dict], error_log: list[str], filename: str
) -> list[str]:
    tar = tarfile.open(filename, "w:gz")
    for dir, urls in manifest.items():
        tar.makedir(dir)
        for url in urls:
            response = requests.get(url)
            if response.status_code != 200:
                error_log(
                    f"Could not download {url}: HTTP status code = {response.status_code}"
                )
                continue

            content = io.BytesIO(response.content)

            data_filename = os.path.basename(url)
            if "Content-Disposition" in response.headers:
                # extract filename from Content-Disposition header
                content_disposition = response.headers["Content-Disposition"]
                data_filename = content_disposition.split("filename=")[1].strip('";')

            tar_info = tarfile.TarInfo(dir + "/" + data_filename)
            tar_info.size = len(content)
            tar.addfile(tar_info, fileobj=content)
