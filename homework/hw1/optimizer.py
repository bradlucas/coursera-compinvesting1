#!/bin/python

import sys
import getopt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
# import matplotlib.pyplot as plt
# import pandas as pd
import numpy as np


def fmt_date(dt):
    return dt_start.strftime("%B %-d, %Y")


def build_daily_return(na_normalized_price):
    na_daily_return = na_normalized_price.copy()
    tsu.returnize0(na_daily_return)
    return na_daily_return


def volatility_stddev(na_daily_return):
    return np.std(na_daily_return)


def avg_daily_return(na_daily_return):
    return np.mean(na_daily_return)


def sharpe_ratio(avg_daily_returns, portfolio_stddev, num_days):
    # => (average_daily_returns / portfolio_stddev) * sqrt(days)
    return (avg_daily_returns / portfolio_stddev) * np.sqrt(num_days)


def cumulative_daily_return(t, daily_rets):
    if t == 0:
        return (1 + daily_rets[0])
    return (cumulative_daily_return(t-1, daily_rets) * (1 + daily_rets[t]))


def build_normalized_price(dt_start, dt_end, ls_symbols, lf_allocations):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    # >>> d_data.keys()
    # ['volume', 'high', 'low', 'actual_close', 'close', 'open']
    # >>> type(d_data['close'])
    # <class 'pandas.core.frame.DataFrame'>
    #
    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    # --------------------------------------------------
    # Normalized Data
    #
    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]
    return na_normalized_price


def calc_cumulative_ret(t, lf_returns):
    if t == 0:
        return (1 + lf_returns[0])
    return calc_cumulative_ret(t-1, lf_returns) * (1 + lf_returns[t])


def simulate(dt_start, dt_end, ls_symbols, lf_allocations):
    # Build normalized price
    na_normalized_price = build_normalized_price(dt_start, dt_end, ls_symbols, lf_allocations)

    # Multiply rows by weights/allocations
    na_weighted_price = na_normalized_price * lf_allocations

    # Caluate values using row-wise sum
    na_portfolio_value = na_weighted_price.copy().sum(axis=1)

    # Calculate the daily returns
    # daily_ret = build_daily_return(na_portfolio_value)
    na_portf_rets = na_portfolio_value.copy()
    tsu.returnize0(na_portf_rets)

    vol = volatility_stddev(na_portf_rets)
    avg_ret = avg_daily_return(na_portf_rets)
    sharpe = sharpe_ratio(avg_ret, vol, 252)
    cum_ret = calc_cumulative_ret(na_portf_rets.size - 1, na_portf_rets)

    return [vol, avg_ret, sharpe, cum_ret]


def print_output(dt_start, dt_end, ls_symbols, lf_allocations, vol, daily_ret, sharpe, cum_ret):
    print("Start Date: %s" % fmt_date(dt_start))
    print("End Date: %s" % fmt_date(dt_end))
    print("Symbols: %s" % ls_symbols)
    print("Optimal Allocations: %s" % lf_allocations)
    print("Sharpe Ratio: %s" % sharpe)
    print("Volatility (stdev of daily returns):  %s" % vol)
    print("Average Daily Return:  %s" % daily_ret)
    print("Cumulative Return:  %s" % cum_ret)


def incs():
    return [x / 10.0 for x in range(0, 11)]


def optimize(dt_start, dt_end, ls_symbols):
    # try all the permutations of of 4 allocations ranging from 0.0 -> 1 in .1 increments
    # return the best or the one with the highest sharpe ratio
    cur_max_sharpe = 0
    cur_max_allocations = []
    for i in incs():
        for j in incs():
            for k in incs():
                for l in incs():
                    if sum([i, j, k, l]) == 1.0:
                        vol, avg_ret, sharpe, cum_ret = simulate(dt_start, dt_end, ls_symbols, [i, j, k, l])
                        if sharpe>cur_max_sharpe:
                            cur_max_sharpe = sharpe
                            cur_max_allocations = [i, j, k, l]
    return [cur_max_sharpe, cur_max_allocations]


def setup():
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)
    ls_symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']
    lf_allocations = [0.4, 0.4, 0.0, 0.2]


def test_run():
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)
    ls_symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']
    lf_allocations = [0.4, 0.4, 0.0, 0.2]
    lf_Stats = simulate(dt_start, dt_end, ls_symbols, lf_allocations)
    vol = lf_Stats[0]
    daily_ret = lf_Stats[1]
    sharpe = lf_Stats[2]
    cum_ret = lf_Stats[3]
    print_output(dt_start, dt_end, ls_symbols, lf_allocations, vol, daily_ret, sharpe, cum_ret)

    # Start Date: 2011-01-01 00:00:00
    # End Date: 2011-12-31 00:00:00
    # Symbols: ['AAPL', 'GLD', 'GOOG', 'XOM']
    # Optimal Allocations: [0.4, 0.4, 0.0, 0.2]
    # Sharpe Ratio: 1.0241954103
    # Volatility (stdev of daily returns):  0.0101467067654
    # Average Daily Return:  0.000657261102001
    # Cumulative Return:  1.16487261965

    best_sharpe, best_allocations = optimize(dt_start, dt_end, ls_symbols)
    print "Optimal Allocations: %s" % best_allocations
    print "--------------------------------------------------"

    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    ls_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
    lf_allocations = [0.0, 0.0, 0.0, 1.0]
    lf_Stats = simulate(dt_start, dt_end, ls_symbols, lf_allocations)
    vol = lf_Stats[0]
    daily_ret = lf_Stats[1]
    sharpe = lf_Stats[2]
    cum_ret = lf_Stats[3]
    print_output(dt_start, dt_end, ls_symbols, lf_allocations, vol, daily_ret, sharpe, cum_ret)

    # Start Date: 2010-01-01 00:00:00
    # End Date: 2010-12-31 00:00:00
    # Symbols: ['AXP', 'HPQ', 'IBM', 'HNZ']
    # Optimal Allocations: [0.0, 0.0, 0.0, 1.0]
    # Sharpe Ratio: 1.29372873378
    # Volatility (stdev of daily returns):  0.00924299255937
    # Average Daily Return:  0.000756285585593
    # Cumulative Return:  1.1960583568
    best_sharpe, best_allocations = optimize(dt_start, dt_end, ls_symbols)
    print "Optimal Allocations: %s" % best_allocations


def run(dt_start, dt_end, ls_symbols):
    best_sharpe, best_allocations = optimize(dt_start, dt_end, ls_symbols)
    lf_Stats = simulate(dt_start, dt_end, ls_symbols, best_allocations)
    vol = lf_Stats[0]
    daily_ret = lf_Stats[1]
    sharpe = lf_Stats[2]
    cum_ret = lf_Stats[3]
    print_output(dt_start, dt_end, ls_symbols, best_allocations, vol, daily_ret, sharpe, cum_ret)


# python optimizer.py startyear startmonth startday endyear endmonth endday symbol1 symbol2 symbol3 symbol4
if __name__ == "__main__":
    # startyear startmonth startday endyear endmonth endday symbol1 symbol2 symbol3 symbol4
    opts, args = getopt.getopt(sys.argv[1:], "")
    if len(args) != 10:
        print "\n\nUsage: python optimizer.py startyear startmonth startday endyear endmonth endday symbol1 symbol2 symbol3 symbol4\n\n"
        sys.exit()

    dt_start = dt.datetime(int(args[0]), int(args[1]), int(args[2]))
    dt_end = dt.datetime(int(args[3]), int(args[4]), int(args[5]))
    ls_symbols = [x.upper() for x in [args[6], args[7], args[8], args[9]]]
    run(dt_start, dt_end, ls_symbols)

# ----------------------------------------------------------------------------------------------------
# Test Runs

# python optimizer.py 2011 1 1 2011 12 31 aapl gld goog xom

# Start Date: January 1, 2011
# End Date: January 1, 2011
# Symbols: ['AAPL', 'GLD', 'GOOG', 'XOM']
# Optimal Allocations: [0.4, 0.4, 0.0, 0.2]
# Sharpe Ratio: 1.02828403099
# Volatility (stdev of daily returns):  0.0101467067654
# Average Daily Return:  0.000657261102001
# Cumulative Return:  1.16487261965
    
# python optimizer.py 2010 1 1 2010 12 31 axp hpq ibm hnz

# Start Date: January 1, 2010
# End Date: January 1, 2010
# Symbols: ['AXP', 'HPQ', 'IBM', 'HNZ']
# Optimal Allocations: [0.0, 0.0, 0.0, 1.0]
# Sharpe Ratio: 1.29889334008
# Volatility (stdev of daily returns):  0.00924299255937
# Average Daily Return:  0.000756285585593
# Cumulative Return:  1.1960583568
