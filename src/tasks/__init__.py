"""
    Entry point to the tasks module
"""
from env import ENV, EDeploymentTier as EDE


class RQueues():
    """ SSOT for redis queue names """
    START_JOBS = "START_JOBS-"+str(ENV.DEPLOYMENT_TIER)
    FINISH_JOBS = "FINISH_JOBS-"+str(ENV.DEPLOYMENT_TIER)
