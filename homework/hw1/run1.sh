#!/bin/bash

# Start Date: January 1, 2011
# End Date: January 1, 2011
# Symbols: ['AAPL', 'GLD', 'GOOG', 'XOM']
# Optimal Allocations: [0.4, 0.4, 0.0, 0.2]
# Sharpe Ratio: 1.02828403099
# Volatility (stdev of daily returns):  0.0101467067654
# Average Daily Return:  0.000657261102001
# Cumulative Return:  1.16487261965

python optimizer.py 2011 1 1 2011 12 31 aapl gld goog xom
