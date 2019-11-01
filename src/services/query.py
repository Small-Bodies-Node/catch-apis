"""
Catch a moving target in survey data.
"""

import re
from typing import List, Any, Optional, Callable, Tuple, Pattern, Match
import uuid

from sbpy.data.names import Names, TargetNameParseError

from .caught import caught
from .database_provider import catch_manager


class TargetTypePatterns:
    # developed with some guidance from sbpy code.
    temporary_designation: str = (
        '(18|19|20)[0-9][0-9] [A-Z]{1,2}([1-9][0-9]{0,2})?'
    )
    name: str = "['`]?[dvA-Z][A-Z]*['`]?[a-z][a-z]*['`]?[^0-9]*"
    cometary_fragment: str = '-[A-Z]{1,2}'

    cometary: Pattern = re.compile(
        # all comets start with 123P, 123D, or P/, C/, D/, X/
        # allow fragments like 73P-B
        # First check for 99P/2030 A2, then P/2030 A2
        # This avoids nonsense like 32C/Asdf
        ('(^([1-9][0-9]*[PD]({frag})?)(/(({temp}({frag})?)))?)|({name})'
         '|(^[PDCX]/{temp}({frag})?)'
         )
        .format(frag=cometary_fragment, temp=temporary_designation,
                name=name)
    )

    asteroidal: Pattern = re.compile(
        '(^\([1-9][0-9]*\)( {name})?)|(^[1-9][0-9]*)|(^{temp})'
        .format(name=name, temp=temporary_designation)
    )

    interstellar_object: Pattern = re.compile(
        '[1-9][0-9]*I((/{name})|(/{temp}))'.format(
            name=name, temp=temporary_designation)
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
                save_to: Optional[uuid.UUID]) -> bool:
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
    for target_type, pattern in (('comet', TargetTypePatterns.cometary),
                                 ('asteroid', TargetTypePatterns.asteroidal),
                                 ('interstellar object',
                                  TargetTypePatterns.interstellar_object)):
        m: Union[Match, None] = pattern.match(name)
        if m is not None:
            match = m[0]
            break
    if m is None:
        target_type = 'unknown'
        match = ''

    return target_type, match
