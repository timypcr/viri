#!/bin/bash

if [ ! `which debuild` ]
then
    echo "debuild not found. Install it before running this script."
    exit 1
fi

BUILD_DIR=`dirname $0`/build
PY_VER="3.2.1"
PY_DIR="Python-$PY_VER"
PY_SRC="$PY_DIR.tar.bz2"

if [ ! -d $BUILD_DIR ]
then
    mkdir $BUILD_DIR
fi
cd $BUILD_DIR

if [ ! -f $PY_SRC ]
then
    wget http://www.python.org/ftp/python/$PY_VER/$PY_SRC
fi

rm -rf $PY_DIR
tar -xjvf $PY_SRC

mkdir $PY_DIR/debian/
cd ..
cp changelog compat control control.in control.stdlib copyright postinst postrm prerm rules $BUILD_DIR/$PY_DIR/debian/

cd $BUILD_DIR/$PY_DIR
debuild

