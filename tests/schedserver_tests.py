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
>>> from viri import orm
>>> from viri.objects import File, Job, objects

# Initialize
>>> db_file = tempfile.NamedTemporaryFile(prefix='viri_db_')
>>> db = orm.Database(db_file.name)
>>> for obj in objects:
...     obj.create_table(db)
>>> script = File.create(db, dict(
...     file_name='script1',
...     content=b'''
... class ViriScript:
...     def run(self):
...         return 'Hello world!'
... '''))
>>> script = File.create(db, dict(
...     file_name='script2',
...     content=b'''
... class ViriScript:
...     def run(self):
...         return 'Hello world!'
... '''))
>>> script = File.create(db, dict(
...     file_name='script3',
...     content=b'''
... class ViriScript:
...     def run(self):
...         return 'Hello world!'
... '''))
>>> script = File.create(db, dict(
...     file_name='script4',
...     content=b'''
... class ViriScript:
...     def run(self):
...         return 'Hello world!'
... '''))
>>> script = File.create(db, dict(
...     file_name='script5',
...     content=b'''
... class ViriScript:
...     def run(self):
...         return 'Hello world!'
... '''))

# Insert jobs
>>> job = Job.create(db, dict(
...    file_name_or_id='script1',
...     minute='*',
...     hour='*',
...     month_day='*',
...     month='*',
...     week_day='*',
...     year='*'))
>>> job = Job.create(db, dict(
...    file_name_or_id='script2',
...     minute='23',
...     hour='23',
...     month_day='30',
...     month='4',
...     week_day='*',
...     year='2011'))
>>> job = Job.create(db, dict(
...    file_name_or_id='script3',
...     minute='23',
...     hour='23',
...     month_day='*',
...     month='*',
...     week_day='6',
...     year='*'))
>>> job = Job.create(db, dict(
...    file_name_or_id='script4',
...     minute='59',
...     hour='23',
...     month_day='31',
...     month='12',
...     week_day='*',
...     year='*'))
>>> job = Job.create(db, dict(
...    file_name_or_id='script5',
...     minute='0',
...     hour='0',
...     month_day='1',
...     month='1',
...     week_day='*',
...     year='*'))

# Get jobs for specific dates and times
>>> sorted(map(lambda x: x.file_name_or_id, Job.run_now(db, datetime.datetime(2011, 4, 30, 23, 23))))
['script1', 'script2', 'script3']
>>> sorted(map(lambda x: x.file_name_or_id, Job.run_now(db, datetime.datetime(1999, 12, 31, 23, 59))))
['script1', 'script4']
>>> sorted(map(lambda x: x.file_name_or_id, Job.run_now(db, datetime.datetime(2000, 1, 1, 0, 0))))
['script1', 'script5']

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

