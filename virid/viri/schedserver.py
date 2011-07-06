import datetime
import logging
import time
#import threading
from viri.objects import Script, Job


SLEEP_TIME = 5 # seconds


class SchedServer:
    """Daemon which simulates the cron application, but instead of executing
    shell commands, it executes viri tasks. 
    """
    def __init__(self, db, context):
        """Initializes the SchedServer, by setting the path of the jobs file
        """
        self.db = db
        self.context = context

    def run(self, now):
        for job in Job.run_now(self.db, now):
            # FIXME use thread?  threading.Thread(target=job).start()
            try:
                Script.execute(self.db, job.filename_or_id, (), self.context)
            except Exception as exc:
                logging.critical('Error running scheduled task {}: {}'.format(
                    job.filename_or_id, exc))

    def start(self):
        """Starts the SchedServer. It gets the current time (date, hour and
        minute), and checks for all jobs in the jobs file, if any of them
        has to be executed in the current minute, and executes them.

        Jobs are called in new threads, so they shouldn't block the execution
        process. But in case the scheduling process is delayed more than a
        minute, it doesn't skip any minute, and it executes tasks even if they
        are delayed.
        """
        now = datetime.datetime.now()
        if now.second:
            time.sleep(60 - now.second)
            now = now.replace(second=0,
                microsecond=0) + datetime.timedelta(minutes=1)

        while True: # TODO allow terminating by signal
            try:
                self.run(now)
            except Exception as exc:
                logging.critical('Uncaught error running jobs: %s' % str(exc))

            now += datetime.timedelta(minutes=1)
            while datetime.datetime.now() < now:
                time.sleep(SLEEP_TIME)

