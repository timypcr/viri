# Copyright 2011, Marc Garcia <garcia.marc@gmail.com>
#
# This file is part of Viri.
#
# Viri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Viri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Viri.  If not, see <http://www.gnu.org/licenses/>.

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

