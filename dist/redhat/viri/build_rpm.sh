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

PACKAGE_NAME=viri
PACKAGE_VERSION=0.1
PATH_TO_SOURCE_CODE_ROOT=../../..

function create_local_rpm_tree_if_necessary {
	if [ ! -d "$HOME/rpmbuild/SOURCES/" ];
		then rpmdev-setuptree
	fi
}

function generate_and_copy_files {
	if [ -d "/tmp/$PACKAGE_NAME-$PACKAGE_VERSION" ];
		then rm -rf /tmp/$PACKAGE_NAME-$PACKAGE_VERSION
	fi

	mkdir /tmp/$PACKAGE_NAME-$PACKAGE_VERSION
	cp -R $PATH_TO_SOURCE_CODE_ROOT/* /tmp/$PACKAGE_NAME-$PACKAGE_VERSION
	cd /tmp
	tar -cjvf $HOME/rpmbuild/SOURCES/$PACKAGE_NAME-$PACKAGE_VERSION.tar.bz2 $PACKAGE_NAME-$PACKAGE_VERSION/*
	cd -
}

function create_rpm {
	QA_RPATHS=$[ 0x0001|0x0010 ] rpmbuild -bb --sign $PACKAGE_NAME.spec
}

create_local_rpm_tree_if_necessary
generate_and_copy_files
create_rpm
