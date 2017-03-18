#!/bin/bash

python ./bollinger-events-orders.py 01-01-2008 12-31-2009 20


#!/bin/bash

# ./run.sh 01-01-2008 12-31-2009 5 50000

# event_amount
START=01-01-2008
END=12-31-2009
LOOKBACK=20
BALANCE=100000


CMD="python .bollinger-events-orders.py $START $END $LOOKBACK && python ../hw4/marketsim.py $BALANCE "orders.csv" values.csv &&  python ../hw4/analyze.py values.csv \$SPX"
echo $CMD

python ./bollinger-events-orders.py $START $END $LOOKBACK && python ../hw4/marketsim.py $BALANCE "orders.csv" values.csv &&  python ../hw4/analyze.py values.csv \$SPX
