# Licensed with the 3-clause BSD license.  See LICENSE for details.

import re
from enum import Enum
from typing import Pattern

from astropy.time import Time
from astropy.coordinates import Latitude, Longitude
import astropy.units as u


def parse_ra(ra: str) -> Longitude:
    """Parse a string as an angle of right ascension.

    The string may specify the units, see astropy.coordinates.Angle() for
    allowed formats.

    If parsable by float(), then degrees are assumed.  Otherise, hour angle is
    assumed.

    Raise ValueError if it cannot be parsed.

    """

    try:
        float(ra)
        ra_unit = u.degree
    except ValueError:
        ra_unit = u.hourangle

    try:
        sanitized_ra = Longitude(ra, ra_unit)
    except Exception as e:
        raise ValueError(f"Invalid ra: {ra}")

    return sanitized_ra


def parse_dec(dec: str) -> Latitude:
    """Parse a string as an angle of declination.

    The string may specify the units, see astropy.coordinates.Angle() for
    allowed formats.

    If units are not specified, then degrees are assumed.

    Raise ValueError if it cannot be parsed.

    """

    try:
        return Latitude(dec, u.deg)
    except ValueError:
        raise ValueError(f"Invalid dec: {dec}")
    except u.UnitsError:
        raise ValueError(f"Invalid units for dec: {dec}")


def parse_date(date: str | None, kind: str) -> str | None:
    """Valid if None or parsable by astropy.time.Time().

    Raises ValueError if not.

    """

    if date is None:
        return None

    try:
        return Time(date)
    except ValueError:
        raise ValueError(f"Invalid {kind}_date: {date}")


"""Target name verification."""


class SSOTargetType(Enum):
    """Possible types of solar system objects within CATCH."""

    ASTEROID = "asteroid"
    COMET = "comet"
    INTERSTELLAR_OBJECT = "interstellar object"
    UNKNOWN = "unknown"


class TargetTypePatterns:
    """Approximate regular expression patterns for small body names."""

    # developed with some guidance from sbpy code.
    temporary_designation: str = (
        "(18|19|20)[0-9][0-9] (([A-Z]{1,2}[1-9][0-9]{0,2})" "|([A-Z][A-Z]))(?![A-Z])"
    )
    cometary_fragment: str = "-[A-Z]{1,2}"
    permanent_cometary_designation: str = "[1-9][0-9]*[PD]({frag})?".format(
        frag=cometary_fragment
    )

    # generous pattern for names
    name: str = r"[A-z \-'`.!|]+"

    cometary: Pattern = re.compile(
        # all comets start with 123P, 123D, or P/, C/, D/, X/
        # allow fragments like 73P-B
        # First check for 99P/2030 A2, then P/2030 A2
        # This avoids nonsense like 32C/Asdf
        (
            # 123P, 73P-B, and allows trailing /name, e.g., 1P/Halley,
            # 9P/Tempel 1, 51P-D/Harrington-D
            r"(^{perm}(?=/{name})?)"
            # P/2001 YX127, allows trailing (name), e.g.,
            # C/2013 US10 (Catalina)
            r"|(^[PDCX]/{temp}({frag})?(?=\s+\({name}\))?)"
            # 7-character comets not working with catch->sbsearch->horizons
            # J95A010, 7-character packed
            # r'|(^[IJK][0-9]{{2,2}}[A-Z][0-9A-z]{{2,2}}[0a-z]$)'
            # 12-character packed designations not supported by Horizons
            # 12-character packed, temporary comet
            # r'|(^[CPDX][IJK][0-9]{{2,2}}[A-Z][0-9A-z]{{2,2}}[0a-z]$)'
            # 12-character packed, temporary comet originally an asteroid
            # r'|(^[CPDX][IJK][0-9]{{2,2}}[A-Z][0-9A-Za-z][0-9][A-Z]$)'
            # 12-character packed, permanent comet
            # r'|(^[0-9]{{4,4}}[CPDX]$(\s+[a-z])?)'
        ).format(
            perm=permanent_cometary_designation,
            frag=cometary_fragment,
            temp=temporary_designation,
            name=name,
        )
    )

    asteroidal: Pattern = re.compile(
        (
            r"(^{temp}$)"  # 2019 DQ123
            # (1234), allows trailing name: (1) Ceres
            r"|(^\([1-9][0-9]*\)(?=\s+{name})?)"
            r"|(^[1-9][0-9]*\b(?!\S)$)"  # 1234
            r"|(^A/{temp}$)"  # A/2019 Q1
            r"|(^A[IJK][0-9]{{2,2}}[A-Z][0-9A-z]{{2,2}}[0a-z]$)"  # AK21E040
            r"|(^[0-9]{{4,4}} (P-L|T-[123])$)"  # 2040 P-L, 3138 T-1
            r"|([IJK][0-9]{{2,2}}[A-Z][0-9A-Za-z][0-9][A-Z]$)"  # J95X00A
            r"|((PL|T[123])S[0-9]{{4,4}}$)"  # PLS2040, T1S3138
        ).format(temp=temporary_designation, name=name)
    )

    interstellar_object: Pattern = re.compile(
        (r"([1-9][0-9]*I(?=/{name})?)" r"|(^[0-9]{{4,4}}I$)").format(name=name)
    )


def parse_target_name(name: str) -> tuple[SSOTargetType, str]:
    """Parse moving target name.


    Parameters
    ----------
    name : str
        String to test.


    Returns
    -------
    target_type : SSOTargetType
        The type of target.

    match : str
        String that matched the target type format.  Blank for unknown.


    Raises
    ------
    ValueError for empty strings or ambiguous target types.

    """

    name = name.strip()
    if name == "":
        raise ValueError("Invalid target: empty string")

    # test target patterns until there is a match
    target_patterns = [
        (SSOTargetType.COMET, TargetTypePatterns.cometary),
        (SSOTargetType.ASTEROID, TargetTypePatterns.asteroidal),
        (
            SSOTargetType.INTERSTELLAR_OBJECT,
            TargetTypePatterns.interstellar_object,
        ),
    ]

    match = ""
    for target_type, pattern in target_patterns:
        m = pattern.match(name)

        if m is not None:
            # remove parentheses from queries like (123)
            match = m[0].strip().lstrip("(").rstrip(")")
            break
    else:
        target_type = SSOTargetType.UNKNOWN

    if match == "":
        raise ValueError(
            "Target names may be ambiguous (e.g., Encke is the name of a comet and "
            "an asteroid) and are not supported.  Use the target's designation or "
            "permanent catalog ID (e.g., 2P or 9134)."
        )

    return target_type, match
