from uuid import UUID
from astropy.time import Time
from ..config.env import ENV
from .queue import JobsQueue


def queue() -> dict[str, bool | list[dict[str, str | int]]]:
    """Controller to return summary of job queue.


    Returns
    -------
    status : dict
        - depth: number of jobs allowed in the queue
        - full: True if the queue is full
        - jobs: list of job summaries
            - prefix: job ID prefix
            - position: queue position
            - enqueued_at: time the query was added to the queue
            - status: the job's status

    """

    jobs: list[dict[str, str | int]] = []
    q = JobsQueue()
    for job in q.jobs:
        catch_job_id: UUID = job.args[0]

        jobs.append(
            {
                "prefix": catch_job_id.hex[:8],
                "position": job.get_position(),
                "enqueued_at": Time(job.enqueued_at).iso,
                "status": job.get_status(),
            }
        )

    return {"depth": ENV.REDIS_JOBS_MAX_QUEUE_SIZE, "full": q.full, "jobs": jobs}
