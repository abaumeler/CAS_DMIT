#!/bin/bash
########################
# setup test environment
########################

if [ ! -d /testing/input ]; then
  mkdir -p ../testing/input;
fi

if [ ! -d /testing/history ]; then
  mkdir -p ../testing/history;
fi

if [ ! -d /testing/failed ]; then
  mkdir -p ../testing/failed;
fi

if [ ! -d /testing/failed ]; then
  mkdir -p ../testing/wait;
fi

cp ../testdata/* ../testing/failed