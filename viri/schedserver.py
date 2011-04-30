import os
import datetime
import time
import threading

SLEEP_TIME = 5 # seconds

# TODO make all settings arguments
SCHED_DIR = 'sched'
JOBS_FILE = 'jobs'

class InvalidCronSyntax(Exception):
    """Error when parsing a cron syntax execution schedule
    """
    pass


class Job:
    """Represents a scheduled execution of a script
    """
    def __init__(self, cron_line):
        COMMENT_CHAR = '#'
        DIVISION_CHAR = ' '

        to_int = lambda x: x if x == '*' else int(x)

        cron_def = cron_line
        if COMMENT_CHAR in cron_def:
            cron_def = cron_def.split(COMMENT_CHAR)[0]

        cron_def = cron_def.strip()
        if cron_def:
            cron_def = cron_def.split(DIVISION_CHAR)
            self.task_id = cron_def.pop()
            try:
                (self.minute, self.hour, self.day, self.month, self.weekday
                    ) = map(to_int, cron_def)
            except ValueError:
                raise InvalidCronSyntax('Invalid cron syntax on "%s"' % cron_line)

    def __call__(self):
        """Method executed when the job has to run. It executes the task
        specified in the cron definition
        """
        return self.task_id # FIXME execute the task, not return the id

    def has_to_run(self, now):
        """Returns a boolean representing if the job has to run in the
        current time, specified by now.
        """
        # TODO make this method understand more syntax, not just numbers
        # and the wildcard "*" representing all
        #
        # See complete syntax at http://en.wikipedia.org/wiki/Cron#Format

        if self.month not in ('*', now.month):
            return False
        elif self.weekday not in ('*', (now.weekday() + 1) % 7):
            # In cron, Sunday is 0, but in Python is 6
            return False
        elif self.day not in ('*', now.day):
            return False
        elif self.hour not in ('*', now.hour):
            return False
        elif self.minute not in ('*', now.minute):
            return False
        else:
            return True


class SchedServer:
    """
    """
    def __init__(self):
        self.sched_dir = SCHED_DIR
        self.jobs_file = os.path.join(self.sched_dir, JOBS_FILE)

        if not os.path.isdir(self.sched_dir):
            os.mkdir(self.sched_dir)

    def start(self):
        """
        """
        now = datetime.datetime.now()
        if now.second:
            time.sleep(60 - now.second)
            now = now.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)

        while True: # TODO allow terminating by signal
            with open(self.job_file, 'r') as job_file:
                for job_def in job_file.readlines():
                    job = Job(job_def)
                    if job.has_to_run(now):
                        threading.Thread(target=job).start()

            now += datetime.timedelta(minutes=1)
            while datetime.datetime.now() < now:
                time.sleep(SLEEP_TIME)

