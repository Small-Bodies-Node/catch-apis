'''
    Dud test to practice pipeline-test failures
'''

import pytest


@pytest.mark.xfail
def test_will_fail() -> None:
    assert 1 == 2
