#!/bin/bash

mkdir bin
cp ../virid/bin/virid ./bin/
mkdir viri
cp ../virid/viri/*.py ./viri/
./setup.py build
rm -rf ./bin ./viri

