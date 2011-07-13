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

r"""
>>> import datetime
>>> import tempfile
>>> import shutil
>>> from viri import scriptmanager
>>> from viri import schedserver

>>> script_dir = tempfile.mkdtemp(prefix='viri-tests-scripts-')
>>> data_dir = tempfile.mkdtemp(prefix='viri-tests-data-')
>>> info_dir = tempfile.mkdtemp(prefix='viri-tests-info-')
>>> context = {}
>>> script_manager = scriptmanager.ScriptManager(
...     script_dir, info_dir, context)

###########
### Job ###
###########

# Execute every minute
>>> job = schedserver.Job('* * * * * hash', script_manager)
>>> job.has_to_run(datetime.datetime(2011, 4, 30, 23, 23, 12))
True
>>> job.has_to_run(datetime.datetime(1999, 12, 31, 23, 59, 59))
True
>>> job.has_to_run(datetime.datetime(2000, 1, 1, 0, 0, 0))
True

# Execute on specific date and time
>>> job = schedserver.Job('23 23 30 04 * hash', script_manager)
>>> job.has_to_run(datetime.datetime(2011, 4, 30, 23, 23, 12))
True
>>> job.has_to_run(datetime.datetime(1999, 12, 31, 23, 59, 59))
False
>>> job.has_to_run(datetime.datetime(2000, 1, 1, 0, 0, 0))
False

# Execute on last minute of the year
>>> job = schedserver.Job('59 23 31 12 * hash', script_manager)
>>> job.has_to_run(datetime.datetime(2011, 4, 30, 23, 23, 12))
False
>>> job.has_to_run(datetime.datetime(1999, 12, 31, 23, 59, 59))
True
>>> job.has_to_run(datetime.datetime(2000, 1, 1, 0, 0, 0))
False

# Execute on first minute of the year
>>> job = schedserver.Job('00 00 01 01 * hash', script_manager)
>>> job.has_to_run(datetime.datetime(2011, 4, 30, 23, 23, 12))
False
>>> job.has_to_run(datetime.datetime(1999, 12, 31, 23, 59, 59))
False
>>> job.has_to_run(datetime.datetime(2000, 1, 1, 0, 0, 0))
True

###################
### SchedServer ###
###################

>>> sched_server = schedserver.SchedServer(data_dir, script_manager)

################
### clean up ###
################

>>> shutil.rmtree(script_dir)
>>> shutil.rmtree(data_dir)
>>> shutil.rmtree(info_dir)

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

