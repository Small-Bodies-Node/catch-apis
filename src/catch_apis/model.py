# Licensed with the 3-clause BSD license.  See LICENSE for details.


class DataProducts:
    """Specifications for data to download.


    Parameters
    ----------
    images : list of dict
        List of image specifications:
            - observation_id: (required)
            - cutout: (optional)
                - ra: right ascension, degrees
                - dec: declination, degrees
                - size: cutout size, degrees
                - format: cutout format

    previews : bool
        Also download preview (JPEG) images.

    """

    def __init__(self, images: list[dict], previews: bool):
        self.images = images
        self.previews = previews
        self.observation_ids = list(
            set([image["observation_id"] for image in self.images])
        )

    # def cutout_spec(self, observation_id: int) -> dict[str, float] | None:
    #     """Get the user's requested cutout parameters.

    #     Parameters
    #     ----------
    #     observation_id : int
    #         The observation ID in question.

    #     Returns
    #     -------
    #     spec : dict or None
    #         The specifications (ra, dec, size) or None, if no cutout requested.

    #     """

    #     return self.images_by_id.get(observation_id, {}).get("cutout")
