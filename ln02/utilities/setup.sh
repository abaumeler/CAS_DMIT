#!/bin/bash
########################
# setup test environment
########################

rm -rf ./testing/wait
rm -rf ./testing/input
rm -rf ./testing/rawdata


if [ ! -d /testing/input ]; then
  mkdir -p ./testing/input;
fi

if [ ! -d /testing/history ]; then
  mkdir -p ./testing/history;
fi

if [ ! -d /testing/failed ]; then
  mkdir -p ./testing/failed;
fi

if [ ! -d /testing/failed ]; then
  mkdir -p ./testing/wait;
fi

cp ./testdata/*.pdf ./testing/failed
cp ./testdata/*.rdf ./testing/failed
cp -rf ./testdata/rawdata ./testing/rawdata
