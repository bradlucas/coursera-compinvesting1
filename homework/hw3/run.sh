#!/bin/bash

# run.sh 1000000 orders.csv \$SPX

BALANCE=$1
ORDERS=$2
INDEX=$3

rm -f values.csv
python marketsim.py $BALANCE $ORDERS values.csv && python analyze.py values.csv $INDEX

