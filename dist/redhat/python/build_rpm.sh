#!/bin/bash

# Copyright 2011, Jesús Corrius <jcorrius@gmail.com>
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

PACKAGE_NAME=python-3.2.1-viri
PYTHON_VERSION=3.2.1


function create_local_rpm_tree_if_necessary {
	if [ ! -d "$HOME/rpmbuild/SOURCES/" ];
		then rpmdev-setuptree
	fi
}

function download_and_copy_files {
	wget http://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.bz2 -O $HOME/rpmbuild/SOURCES/Python-$PYTHON_VERSION.tar.bz2
}

function create_rpm {
	QA_RPATHS=$[ 0x0001|0x0010 ] rpmbuild -ba --sign $PACKAGE_NAME.spec
}

create_local_rpm_tree_if_necessary
download_and_copy_files
create_rpm
