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

PACKAGE_NAME=viri-release

function create_local_rpm_tree_if_necessary {
	if [ ! -d "$HOME/rpmbuild/SOURCES/" ];
		then rpmdev-setuptree
	fi
}

function copy_files {
	cp RPM-GPG-KEY-VIRI $HOME/rpmbuild/SOURCES
	cp viri.repo $HOME/rpmbuild/SOURCES
}

function create_rpm {
	rpmbuild -ba --sign $PACKAGE_NAME.spec
}

create_local_rpm_tree_if_necessary
copy_files
create_rpm
