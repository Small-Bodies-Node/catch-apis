"""
    Entry point to the tasks module
"""
from env import ENV, EDeploymentTier as EDE


class RQueues():
    """ SSOT for redis queue names """
    JOBS = "JOBS-"+str(ENV.DEPLOYMENT_TIER)
    TASK_MESSAGES = "TASK_MESSAGES-"+str(ENV.DEPLOYMENT_TIER)
