import os
import re
from numpy import full
import pytest
import requests
from services.query import TargetTypePatterns

# Test target names / designations (packed and unpacked) with the
# catch-apis target type patterns.  The target type patterns identify
# the target type (asteroid, comet, or interstellar object) so that
# an appropriate API call to JPL Horizons may be made.


# Add specific asteroids to this list
ASTEROIDS = set([
    '2019 DQ123',
    '(1234)',
    '1234',
    'A/2019 Q1',
    '2040 P-L',
    '3138 T-1',
    'J95X00A',
    'PLS2040',
    'T1S3138',
    '2021 HS',
])

# Add specific comets to this list
COMETS = set([
    '1P/Halley',
    '3D/Biela',
    '6P/d\'Arrest',
    '9P/Tempel 1',
    '73P/Schwassmann-Wachmann 3-C',
    '73P-C/Schwassmann-Wachmann 3-C',
    '73P-BB',
    '122P/de Vico',
    '322P',
    'P/1994 N2 (McNaught-Hartley)',
    'P/2001 YX127 (LINEAR)',
    'P/2021 HS',
    'C/2001 A2-A (LINEAR)',
    'P/2010 WK (LINEAR)',
    'C/2013 US10',
    'C/2015 V2 (Johnson)',
    'C/2014 S2 (Pan-STARRS)',
    'C/2014 S2 (PanSTARRS)',
    'J95A010',
    'J94P01b',
    'J94P010',
    'K48X130',
    'K33L89c',
    'K88AA30',
])

# Add specific interstellar objects to this list
INTERSTELLAR_OBJECTS = set([
    '0001I',
    '1I/`Oumuamua',
    '0002I',
    '2I/Borisov'
])

# Add search strings to send to the SBN name resolution tool to this list.
# Try to get some comets and the interstellar objects.
RESOLVE_NAMES = [
    '65P',
    'Ceres',
    'encke',
    'C/2013 US10',
    'oumuamua',
    'borisov',
    '2019 XS'
]

RESOLVED_NAMES = []
for query in RESOLVE_NAMES:
    r = requests.get('https://name-resolution-tool.astro.umd.edu/name',
                     params={'name': query})
    matches = r.json()['matches']
    assert len(matches) > 0
    RESOLVED_NAMES.extend(matches)


# Also add all numbered asteroids from this list
path = os.path.dirname(__file__)
with open(f'{path}/asteroid_names.txt', 'r') as inf:
    for line in inf:
        if line[0] == '#':
            continue
        ASTEROIDS.add(line[:39].strip())

# Add asteroids, mostly temporary designations, from this list
path = os.path.dirname(__file__)
with open(f'{path}/asteroid_closest.txt', 'r') as inf:
    for line in inf:
        if line[0] == '#':
            continue
        ASTEROIDS.add(line[54:67].strip())

# add objects from the cometary orbital elements list
# this list has comets (C/, P/, and D/), but also asteroids
# (A/ objects), and interstellar objects (I/ objects)
with open(f'{path}/CometEls.txt', 'r') as inf:
    for line in inf:
        if line[0] == '#':
            continue
        packed = line[:13].strip()
        full_name = line[102:159].strip()
        if full_name[0] == 'A':
            ASTEROIDS.add(packed)
            ASTEROIDS.add(full_name)
        elif packed[4] == 'I':
            INTERSTELLAR_OBJECTS.add(packed)
            INTERSTELLAR_OBJECTS.add(full_name)
        else:
            COMETS.add(full_name)

            # packed cometary designations not working in CATCH->sbsearch->Horizons
            if len(packed) > 7:
                continue

            # # permanent designation with a fragment, does not work at Horizons
            # if packed[0].isdigit() and len(packed) == 12:
            #     continue

            # # we left-strip 0s because Horizons fails for queries like '0001P'
            COMETS.add(packed.lstrip('0'))


@pytest.mark.parametrize('target', ASTEROIDS)
def test_asteroid(target):
    "Verify that the asteroid string parses as an asteroid and not something else."
    assert re.match(TargetTypePatterns.asteroidal, target)
    assert re.match(TargetTypePatterns.cometary, target) is None
    assert re.match(TargetTypePatterns.interstellar_object, target) is None


@pytest.mark.parametrize('target', COMETS)
def test_comet(target):
    "Verify that the comet string parses as an comet and not something else."
    assert re.match(TargetTypePatterns.asteroidal, target) is None
    assert re.match(TargetTypePatterns.cometary, target)
    assert re.match(TargetTypePatterns.interstellar_object, target) is None


@pytest.mark.parametrize('target', INTERSTELLAR_OBJECTS)
def test_interstellar_object(target):
    "Verify that the interstellar object string parses as an ISO and not something else."
    assert re.match(TargetTypePatterns.asteroidal, target) is None
    assert re.match(TargetTypePatterns.cometary, target) is None
    assert re.match(TargetTypePatterns.interstellar_object, target)


@pytest.mark.remote
@pytest.mark.parametrize('match', RESOLVED_NAMES)
def test_via_name_resolution_tool(match):
    "Verify that the SBN name resolution tool types match regexp parsing."
    for match in matches:
        asteroid = re.match(TargetTypePatterns.asteroidal,
                            match['target']) is not None
        comet = re.match(TargetTypePatterns.cometary,
                         match['target']) is not None
        iso = re.match(TargetTypePatterns.interstellar_object,
                       match['target']) is not None

        if match['body_type'] == 'comet':
            assert comet and not (asteroid or iso)
        elif match['body_type'] == 'asteroid':
            assert asteroid and not (comet or iso)
        elif match['body_type'] == 'interstellar_object':
            assert iso and not (asteroid or comet)
        else:
            raise ValueError('unexpected body_type from name resolution tool.')
