import os
import datetime
import logging
import time
import threading
from viritask import Task

SLEEP_TIME = 5 # seconds
JOBS_FILE = '__crontab__' # in data dir


class InvalidCronSyntax(Exception):
    """Error when parsing a cron syntax execution schedule"""
    pass


class Job:
    """Represents a scheduled execution of a script"""
    # TODO improve the way the job is defined. We actually don't know
    # if the job is valid until we check if it has to run
    def __init__(self, cron_def, data_dir):
        """
        """
        COMMENT_CHAR = '#'
        DIVISION_CHAR = ' '
        to_int = lambda x: x if x == '*' else int(x)

        self.data_dir = data_dir

        self.is_valid_job = False

        cron_def = cron_def.strip()
        if COMMENT_CHAR in cron_def:
            cron_def = cron_def.split(COMMENT_CHAR)[0]

        if cron_def:
            cron_def = cron_def.split(DIVISION_CHAR)
            self.task_id = cron_def.pop()
            try:
                (self.minute, self.hour, self.day, self.month, self.weekday
                    ) = map(to_int, cron_def)
                self.is_valid_job = True
            except ValueError:
                raise InvalidCronSyntax() # TODO specific error message

    def __bool__(self):
        """Specifies if the job was a real job, or a comment, a blank line
        or raised an invalid cron syntax. True means it was a valid job.
        """
        return self.is_valid_job

    def __call__(self):
        """Method executed when the job has to run. It executes the task
        specified in the cron definition
        """
        # FIXME capture any exception and log, this should never raise an
        # exception
        task = Task(self.data_dir)
        task.execute(self.task_id)

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
    """Daemon which simulates the cron application, but instead of executing
    shell commands, it executes viri tasks. 
    """
    def __init__(self, data_dir):
        """Initializes the SchedServer, by setting the path of the jobs file
        """
        self.data_dir = data_dir
        self.job_file = os.path.join(data_dir, JOBS_FILE)

    def _run_job(self, job_def, now):
        """Runs a specific job in a new thread, if it has to run in the
        specified time.
        """
        try:
            job = Job(job_def, self.data_dir)
        except InvalidCronSyntax:
            logging.warn('Invalid job definition: %s' % job_def)
        else:
            if job:
                logging.debug('Job definition found: %s' % job_def)
                if job.has_to_run(now):
                    # TODO logging the task name (script file name)
                    # would be more descriptive
                    logging.info(
                        'Running scheduled task %s' % job.task_id)
                    threading.Thread(target=job).start()

    def _run_jobs(self, now):
        """Opens the job files and calls the method _next_job for every
        job definition found. In case an exception is raised from that
        method, it logs the error, and goes on with the next job, as we
        want to execute all possible jobs.
        """
        if os.path.isfile(self.job_file):
            with open(self.job_file, 'r') as job_file:
                for job_def in job_file.readlines():
                    try:
                        self._run_job(job_def.rstrip('\n'), now)
                    except Exception as exc:
                        logging.error('Unknown error executing job %s: %s' % (
                            job_def, str(exc)))
        else:
            logging.debug('Jobs file "%s" not found' % self.job_file)

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
                self._run_jobs(now)
            except Exception as exc:
                logging.critical('Uncaught error running jobs: %s' % str(exc))

            now += datetime.timedelta(minutes=1)
            while datetime.datetime.now() < now:
                time.sleep(SLEEP_TIME)

