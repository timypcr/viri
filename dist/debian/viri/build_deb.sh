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

BUILD_DIR=`dirname $0`/build
VERSION=$1
PROJECT_NAME=Viri-$VERSION

mkdir -p $BUILD_DIR/$PROJECT_NAME/debian
cp -r ./* $BUILD_DIR/$PROJECT_NAME/debian
cp -r ../../../* $BUILD_DIR/$PROJECT_NAME/
cd $BUILD_DIR/$PROJECT_NAME/
debuild
debsign -kEE272E72
