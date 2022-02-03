"""
Catch a moving target in survey data.
"""

import re
from typing import List, Any, Optional, Tuple, Pattern, Match, Union
import uuid

from .caught import caught
from .database_provider import catch_manager
from models.body_type import EBodyType


class TargetTypePatterns:
    """Approximate regular expression patterns for small body names."""
    # developed with some guidance from sbpy code.
    temporary_designation: str = (
        '(18|19|20)[0-9][0-9] (([A-Z]{1,2}[1-9][0-9]{0,2})|([A-Z][A-Z]))(?![A-Z])'
    )
    cometary_fragment: str = '-[A-Z]{1,2}'
    permanent_cometary_designation: str = '[1-9][0-9]*[PD]({frag})?'.format(
        frag=cometary_fragment)

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
            r'(^{perm}(?=/{name})?)'

            # P/2001 YX127, allows trailing (name), e.g.,
            # C/2013 US10 (Catalina)
            r'|(^[PDCX]/{temp}({frag})?(?=\s+\({name}\))?)'

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
        ).format(perm=permanent_cometary_designation,
                 frag=cometary_fragment,
                 temp=temporary_designation,
                 name=name)
    )

    asteroidal: Pattern = re.compile(
        (r'(^{temp}$)'  # 2019 DQ123
         # (1234), allows trailing name: (1) Ceres
         r'|(^\([1-9][0-9]*\)(?=\s+{name})?)'
         r'|(^[1-9][0-9]*\b(?!\S)$)'  # 1234
         r'|(^A/{temp}$)'  # A/2019 Q1
         r'|(^A[IJK][0-9]{{2,2}}[A-Z][0-9A-z]{{2,2}}[0a-z]$)'  # AK21E040
         r'|(^[0-9]{{4,4}} (P-L|T-[123])$)'  # 2040 P-L, 3138 T-1
         r'|([IJK][0-9]{{2,2}}[A-Z][0-9A-Za-z][0-9][A-Z]$)'  # J95X00A
         r'|((PL|T[123])S[0-9]{{4,4}}$)'  # PLS2040, T1S3138
         ).format(temp=temporary_designation,
                  name=name)
    )

    interstellar_object: Pattern = re.compile(
        (r'([1-9][0-9]*I(?=/{name})?)'
         r'|(^[0-9]{{4,4}}I$)').format(name=name)
    )


def query(target: str, job_id: uuid.UUID, source: str,
          cached: bool) -> List[Any]:
    """Run query and return caught data.


    Parameters
    ----------
    target : string
        Target for which to search.

    job_id : uuid.UUID
        Unique job ID.

    source : string
        Observation source.

    cached : bool
        OK to return cached results?


    Returns
    -------
    found : list
        Found observations and metadata.

    """
    with catch_manager(save_log=True) as catch:
        catch.query(target, job_id, source=source, cached=cached)

    found = caught(job_id)
    return found


def check_cache(target: str, source: str,
                save_to: Optional[uuid.UUID]) -> Any:
    """Check CATCH cache for previous query.


    Parameters
    ----------
    target : string
        Target name.

    source : string
        Observation source or ``'any'``.

    save_to : UUID, optional
        Save the cached query under this job ID.


    Returns
    -------
    cached : bool
        ``True`` if ``source`` has already been searched for
        ``target``.  When ``source`` is ``'any'``, then if any source
        was not searched, ``cached`` will be ``False``.

    """

    with catch_manager(save_log=False) as catch:
        cached = catch.check_cache(target, source=source)
        if cached and (save_to is not None):
            catch.query(target, save_to, source=source, cached=True)
    return cached


def parse_target_name(name: str) -> Tuple[str, str]:
    """Parse moving target name.


    Parameters
    ----------
    name : str
        String to test.


    Returns
    -------
    target_type : str
        'asteroid', 'comet', 'interstellar object', or 'unknown'.

    match : str
        String that matched the target type format.  Blank for unknown.

    """

    pattern: Pattern
    match: str
    target_type: str
    name = name.strip()

    for target_type, pattern in (
        (EBodyType.comet.name, TargetTypePatterns.cometary),
        (EBodyType.asteroid.name, TargetTypePatterns.asteroidal),
        (EBodyType.interstellar_object.name, TargetTypePatterns.interstellar_object)
    ):

        m: Union[Match, None] = pattern.match(name)
        if m is not None:
            match = m[0]
            break
        if m is None:
            target_type = EBodyType.unknown.name
            match = ''

    # remove parentheses from queries like (123)
    return target_type, match.strip().lstrip('(').rstrip(')')
