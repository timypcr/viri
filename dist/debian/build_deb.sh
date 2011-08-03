#!/bin/bash

if [ ! $1 ]
then
    echo "Version argument missing"
    exit 1
fi

if [ ! `which debuild` ]
then
    echo "debuild not found. Install it before running this script."
    exit 1
fi

VERSION=$1
PROJECT_NAME=Viri-$VERSION

mkdir -p /tmp/$PROJECT_NAME/debian
cp -r ./* /tmp/$PROJECT_NAME/
cp * /tmp/$PROJECT_NAME/debian/
cd /tmp/$PROJECT_NAME
debuild

