#!/bin/sh

if [ ! $1 ]
then
    echo "Version argument missing"
    exit 1
fi

VERSION=$1
DIR_NAME=Viri-$1

cd ..
cp -r virid $DIR_NAME
tar -cjvf $DIR_NAME.tar.bz2 $DIR_NAME
rm -rf $DIR_NAME/

