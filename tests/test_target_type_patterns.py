import os
import re
from numpy import full
import pytest
from services.query import TargetTypePatterns

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

INTERSTELLAR_OBJECTS = set([
    '0001I',
    '1I/`Oumuamua',
    '0002I',
    '2I/Borisov'
])


path = os.path.dirname(__file__)
with open(f'{path}/asteroid_names.txt', 'r') as inf:
    for line in inf:
        if line[0] == '#':
            continue
        ASTEROIDS.add(line[:40].strip())

path = os.path.dirname(__file__)
with open(f'{path}/asteroid_closest.txt', 'r') as inf:
    for line in inf:
        if line[0] == '#':
            continue
        ASTEROIDS.add(line[54:67].strip())

with open(f'{path}/CometEls.txt', 'r') as inf:
    for line in inf:
        if line[0] == '#':
            continue
        packed = line[:13].strip()
        full_name = line[102:159].strip()
        if full_name[0] == 'A':
            ASTEROIDS.add(packed)
            ASTEROIDS.add(full_name)
        elif full_name[0] == 'I':
            INTERSTELLAR_OBJECTS.add(packed)
            INTERSTELLAR_OBJECTS.add(full_name)
        else:
            COMETS.add(packed)
            COMETS.add(full_name)


@pytest.mark.parametrize('target', ASTEROIDS)
def test_asteroid(target):
    assert re.match(TargetTypePatterns.asteroidal, target)
    assert re.match(TargetTypePatterns.cometary, target) is None
    assert re.match(TargetTypePatterns.interstellar_object, target) is None


@pytest.mark.parametrize('target', COMETS)
def test_comet(target):
    assert re.match(TargetTypePatterns.asteroidal, target) is None
    assert re.match(TargetTypePatterns.cometary, target)
    assert re.match(TargetTypePatterns.interstellar_object, target) is None


@pytest.mark.parametrize('target', INTERSTELLAR_OBJECTS)
def test_comet(target):
    assert re.match(TargetTypePatterns.asteroidal, target) is None
    assert re.match(TargetTypePatterns.cometary, target) is None
    assert re.match(TargetTypePatterns.interstellar_object, target)
