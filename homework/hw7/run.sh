#!/bin/bash

# python ./bollinger-events-orders.py 01-01-2008 12-31-2009 20

# event_amount
START=01-01-2008
END=12-31-2009
LOOKBACK=20
BALANCE=100000


CMD="python .bollinger-events-orders.py $START $END $LOOKBACK && python ../hw3/marketsim.py $BALANCE "orders.csv" values.csv &&  python ../hw3/analyze.py values.csv \$SPX"
echo $CMD

python ./bollinger-events-orders.py $START $END $LOOKBACK && python ../hw3/marketsim.py $BALANCE "orders.csv" values.csv &&  python ../hw3/analyze.py values.csv \$SPX
