#!/bin/python

import sys
import csv
import datetime as dt
import pandas as pd
import math
import numpy as np
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu


def get_prices(dt_start, dt_end, ls_symbols):
    print ls_symbols
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, [ls_symbols], ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    na_prices = d_data['close'].values  # use adjusted closing prices
    return ldt_timestamps, na_prices


def print_output(dt_start, dt_end, sharpe_fund, sharpe_benchmark, total_ret_fund, total_ret_benchmark, stddev_fund,
                 stddev_benchmark, avg_daily_ret_fund, avg_daily_ret_benchmark):
    print
    print 'Details of the Performance of the portfolio :'
    print
    print 'Data Range : ', dt_start, ' to ', dt_end
    print
    print 'Sharpe Ratio of Fund : %-.12g' % sharpe_fund
    print 'Sharpe Ratio of $SPX : %-.12g' % sharpe_benchmark
    print
    print 'Total Return of Fund : %-.12g' % total_ret_fund
    print 'Total Return of $SPX : %-.12g' % total_ret_benchmark
    print
    print 'Standard Deviation of Fund :  %-.12g' % stddev_fund
    print 'Standard Deviation of $SPX : %-.12g' % stddev_benchmark
    print
    print 'Average Daily Return of Fund :  %-.12g' % avg_daily_ret_fund
    print 'Average Daily Return of $SPX : %-.12g' % avg_daily_ret_benchmark


def test_results():
    dt_start = '2011-01-05 16:00:00'
    dt_end = '2011-01-20 16:00:00'
    sharpe_fund = -0.449182051041
    sharpe_benchmark = 0.88647463107
    total_ret_fund = 0.998035
    total_ret_benchmark = 1.00289841449
    stddev_fund = 0.00573613516299
    stddev_benchmark = 0.00492987789459
    avg_daily_ret_fund = -0.000162308588036
    avg_daily_ret_benchmark = 0.000275297459588

    return dt_start, dt_end, sharpe_fund, sharpe_benchmark, total_ret_fund, total_ret_benchmark, stddev_fund, stddev_benchmark, avg_daily_ret_fund, avg_daily_ret_benchmark


# Author     : Tolunay Orkun <tolunay(at)orkun(dot)us>
# Date       : Oct 7, 2013
def read_values(valuesfile):
    """Read values to a Panda DataFrame"""

    li_cols = [0, 1, 2, 3]
    ls_names = ['YEAR', 'MONTH', 'DAY', 'TOTAL']
    d_date_columns = { 'DATE': ['YEAR', 'MONTH', 'DAY']}
    s_index_column = 'DATE'
    df_values = pd.read_csv(valuesfile, \
                            dtype={'TOTAL': np.float64}, \
                            sep=',', \
                            comment='#', \
                            skipinitialspace=True, \
                            header=None, \
                            usecols=li_cols, \
                            names=ls_names, \
                            parse_dates=d_date_columns, \
                            index_col=s_index_column)
    if not df_values.index.is_monotonic:
        df_values.sort_index(inplace=True)

    return df_values

# TODO Not yet working
def read_values_files(filename):
    '''Read the values file produced by marketsim.py
yyyy,mm,dd,balance
    Into a Pandas DataFrame
'''
    value_list = []
    date_list = []
    with open(filename, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
            date = dt.datetime(int(r[0]), int(r[1]), int(r[2]))
            value = float(r[3])
            date_list.append(date)
            value_list.append(value)

    dt_start = date_list[0]
    dt_end = date_list[-1]
    initial_value = value_list[0]

    return dt_start, dt_end, initial_value


def process_values_file(values_file):
    df_values = read_values(values_file)
    dt_start = df_values.index[0]
    dt_end = df_values.index[len(df_values.index) - 1]

    # Extract the values
    na_values = df_values.values * 1.0
    # Normalize (values start a 1
    na_norm_values = na_values / na_values[0, :]
    # Returnize the values
    na_returns = na_norm_values.copy()
    tsu.returnize0(na_returns)

    # Calculate values statistics
    avg_daily_ret_fund = np.mean(na_returns)
    total_ret_fund = np.prod(na_returns + 1.0)
    stddev_fund = np.std(na_returns)
    sharpe_fund = math.sqrt(252.0) * avg_daily_ret_fund / stddev_fund
    return dt_start, dt_end, sharpe_fund, total_ret_fund, stddev_fund, avg_daily_ret_fund


def process_benchmark(dt_start, dt_end, benchmark_symbol):
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end + dt.timedelta(days=1), dt.timedelta(hours=16))
    dt_start = ldt_timestamps[0]
    dt_end = ldt_timestamps[-1]
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['close']
    ldf_data = dataobj.get_data(ldt_timestamps, [benchmark_symbol], ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Extract the data/values
    na_prices = d_data['close'].values
    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_prices / na_prices[0, :]

    na_benchmark_returns = na_normalized_price.copy()
    tsu.returnize0(na_benchmark_returns)

    # Calculate values statistics
    f_benchmark_avg_return = np.mean(na_benchmark_returns)
    total_ret_benchmark = np.prod(na_benchmark_returns + 1.0)
    stddev_benchmark = np.std(na_benchmark_returns)
    sharpe_benchmark = math.sqrt(252.0) * f_benchmark_avg_return / stddev_benchmark

    return dt_start, dt_end, sharpe_benchmark, total_ret_benchmark, stddev_benchmark, f_benchmark_avg_return


def foo(dt_start, dt_end, s_benchmark_symbol):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end + dt.timedelta(days=1), dt_timeofday)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Prepare the symbols to fetch from data source
    ls_symbols = [ s_benchmark_symbol ]

    # Create an object of DataAccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Copying the close price into separate DataFrame
    df_close = d_data['close'].copy()

    # Filling the gaps in data.
    df_close[s_benchmark_symbol] = df_close[s_benchmark_symbol].fillna(method='ffill')
    df_close[s_benchmark_symbol] = df_close[s_benchmark_symbol].fillna(method='bfill')
    df_close[s_benchmark_symbol] = df_close[s_benchmark_symbol].fillna(1.0)

    # Extract just the data
    na_benchmark_close = df_close.values

    # Normalize the price
    na_norm_benchmark_close = na_benchmark_close / na_benchmark_close[0, :]

    # Returnize the values
    na_benchmark_returns = na_norm_benchmark_close.copy()
    tsu.returnize0(na_benchmark_returns)

    # Calculate statistical values
    f_benchmark_avg_return = np.mean(na_benchmark_returns)
    f_benchmark_tot_return = np.prod(na_benchmark_returns + 1.0)
    f_benchmark_stdev = np.std(na_benchmark_returns)
    f_benchmark_sharpe = math.sqrt(252.0) * f_benchmark_avg_return / f_benchmark_stdev

    return f_benchmark_sharpe, f_benchmark_tot_return, f_benchmark_stdev, f_benchmark_avg_return


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print """\
\n
Usage: python analyze.py <values_file> <benchmark_symbol>
"""
        sys.exit(0)


    # dt_start, dt_end, sharpe_fund, sharpe_benchmark, total_ret_fund, total_ret_benchmark, stddev_fund, stddev_benchmark, avg_daily_ret_fund, avg_daily_ret_benchmark = test_results()

    # Read arguments
    values_file = sys.argv[1]
    benchmark_symbol = sys.argv[2]

    dt_start, dt_end, sharpe_fund, total_ret_fund, stddev_fund, avg_daily_ret_fund = process_values_file(values_file)
    print dt_start
    print dt_end

    # sharpe_benchmark, total_ret_benchmark, stddev_benchmark, avg_daily_ret_benchmark = foo(dt_start, dt_end, benchmark_symbol)
    #
    # print_output(dt_start, dt_end, sharpe_fund, sharpe_benchmark, total_ret_fund, total_ret_benchmark, stddev_fund,
    #              stddev_benchmark, avg_daily_ret_fund, avg_daily_ret_benchmark)

    dt_start, dt_end, sharpe_benchmark, total_ret_benchmark, stddev_benchmark, avg_daily_ret_benchmark = process_benchmark(dt_start, dt_end, benchmark_symbol)
    print dt_start
    print dt_end
    print total_ret_benchmark

    print_output(dt_start, dt_end, sharpe_fund, sharpe_benchmark, total_ret_fund, total_ret_benchmark, stddev_fund,
                 stddev_benchmark, avg_daily_ret_fund, avg_daily_ret_benchmark)
