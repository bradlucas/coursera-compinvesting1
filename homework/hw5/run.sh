#!/bin/bash

# ./run.sh 01-01-2010 12-31-2010 20

START=$1
END=$2
LOOKBACK=$3

echo "./run.sh 01-01-2010 12-31-2010 20"
python ./bollinger.py $START $END $LOOKBACK
