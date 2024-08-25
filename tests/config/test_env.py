# Licensed with the 3-clause BSD license.  See LICENSE for details.

import pytest
import numpy as np
from .. import test_client
from catch_apis.config.env import ENV


def test_env():
    assert ENV.REDIS_JOBS == "TEST_JOBS"
