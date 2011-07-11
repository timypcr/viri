def sched_server(db, context, quit):
    """Starts the SchedServer. It gets the current time (date, hour and
    minute), and checks for all jobs in the jobs file, if any of them
    has to be executed in the current minute, and executes them.

    Jobs are called in new threads, so they shouldn't block the execution
    process. But in case the scheduling process is delayed more than a
    minute, it doesn't skip any minute, and it executes tasks even if they
    are delayed.
    """
    import sys
    import datetime
    import time
    import logging

    SLEEP_TIME = 5 # seconds

    def run(now):
        from viri.objects import File, Job

        for job in Job.run_now(db, now):
            try:
                File.execute(db, job.filename_or_id, (), context)
            except Exception as exc:
                logging.critical('Error running scheduled task {}: {}'.format(
                    job.filename_or_id, exc))

    now = datetime.datetime.now()
    if now.second:
        time.sleep(60 - now.second)
        now = now.replace(second=0,
            microsecond=0) + datetime.timedelta(minutes=1)

    while quit.empty():
        run(now)
        now += datetime.timedelta(minutes=1)
        while datetime.datetime.now() < now and quit.empty():
            time.sleep(SLEEP_TIME)

    sys.exit(0)

