#!/bin/bash

if [ ! $1 ]
then
    echo "Version argument missing"
    exit 1
fi

if [ ! `which rpmbuild` ]
then
    echo "rpmbuild not found. Install it before running this script."
    exit 1
fi

VERSION=$1
PROJECT_NAME=Viri-$VERSION

if [[ `cat /proc/version` == *Red\ Hat* ]]
then
    RPM_ROOT=/usr/src/redhat
elif [[ `cat /proc/version` == *Debian* ]]
then
    RPM_ROOT=~/rpmbuild
else
    echo "This script only works in Red Hat or Debian. Aborting."
    exit 1
fi

mkdir -p $RPM_ROOT/SOURCES
mkdir -p $RPM_ROOT/RPMS/noarch

cp viri.spec $RPM_ROOT/SPECS
cp -r ../virid $RPM_ROOT/SOURCES/$PROJECT_NAME
cd $RPM_ROOT/SOURCES/
tar -cjvf $RPM_ROOT/SOURCES/$PROJECT_NAME.tar.bz2 $PROJECT_NAME
rm -rf $RPM_ROOT/SOURCES/$PROJECT_NAME
rpmbuild -bb $RPM_ROOT/SPECS/viri.spec

