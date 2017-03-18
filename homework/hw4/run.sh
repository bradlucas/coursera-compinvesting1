#!/bin/bash

# Example
# ./run.sh 01-01-2008 12-31-2009 5 50000

# event_amount
START=$1
END=$2
EVENT_AMT=$3
BALANCE=$4


CMD="python eventprofiler_output.py $START $END $EVENT_AMT && python marketsim.py $BALANCE "orders-$EVENT_AMT-0.csv" values.csv &&  python analyze.py values.csv \$SPX"
echo $CMD

python eventprofiler-orders.py $START $END $EVENT_AMT && python ../hw3/marketsim.py $BALANCE "orders-$EVENT_AMT-0.csv" values.csv &&  python ../hw3/analyze.py values.csv \$SPX
