#!/bin/bash

# Start Date: January 1, 2010
# End Date: January 1, 2010
# Symbols: ['AXP', 'HPQ', 'IBM', 'HNZ']
# Optimal Allocations: [0.0, 0.0, 0.0, 1.0]
# Sharpe Ratio: 1.29889334008
# Volatility (stdev of daily returns):  0.00924299255937
# Average Daily Return:  0.000756285585593
# Cumulative Return:  1.1960583568

python optimizer.py 2010 1 1 2010 12 31 axp hpq ibm hnz
