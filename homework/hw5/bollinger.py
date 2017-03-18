#!/bin/python

import sys
import datetime as dt

import pandas as pd
import numpy as np

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

# Input
# dt_start, dt_end, loopback_days

# Idea
# Keep three dataframes to contain the moving average, moving stddev and
# bollinger values


def fetch_close_prices(dt_start, dt_end, ls_symbols):
    # Close is at 4 PM
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Get the numpy dnarray of close prices
    na_price = d_data['close'].values

    # Convert to a dataframe
    df_closingprices = pd.DataFrame(na_price, columns=ls_symbols, index=ldt_timestamps)
    return df_closingprices


def build_bollinger_bands(df_closingprices, lookback_days):
    # get the symbols of ot fhte data frame
    ls_symbols = df_closingprices.columns.values
    # print ls_symbols

    # temporary empty np_array
    na_tmp = np.zeros((len(df_closingprices.values), 0))

    df_moving_avg = pd.DataFrame(na_tmp, index=df_closingprices.index)
    df_moving_stddev = pd.DataFrame(na_tmp, index=df_closingprices.index)
    df_bollinger_upper = pd.DataFrame(na_tmp, index=df_closingprices.index)
    df_bollinger_lower = pd.DataFrame(na_tmp, index=df_closingprices.index)
    df_bollinger_value = pd.DataFrame(na_tmp, index=df_closingprices.index)

    k = 1    # multiple of standard deviations

    for symbol in ls_symbols:
        # calculate the moving average
        df_moving_avg[symbol] = df_closingprices[symbol].rolling(window=lookback_days, center=False).mean()
        df_moving_stddev[symbol] = df_closingprices[symbol].rolling(window=lookback_days, center=False).std()

        # @see http://stackoverflow.com/a/37668191
        df_bollinger_upper[symbol] = df_moving_avg[symbol] + df_moving_stddev[symbol] * k
        df_bollinger_lower[symbol] = df_moving_avg[symbol] - df_moving_stddev[symbol] * k

        df_bollinger_value[symbol] = (df_closingprices[symbol] - df_moving_avg[symbol])/df_moving_stddev[symbol]

    return df_moving_avg, df_moving_stddev, df_bollinger_upper, df_bollinger_lower, df_bollinger_value


def main():
    dt_start = dt.datetime.strptime(sys.argv[1], '%m-%d-%Y')
    dt_end = dt.datetime.strptime(sys.argv[2], '%m-%d-%Y')
    n_lookback = int(sys.argv[3])
    # print dt_start, dt_end, n_lookback

    ls_symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT']

    df_closingprices = fetch_close_prices(dt_start, dt_end, ls_symbols)
    # print df_closingprices

    # build bollinger bands
    df_moving_avg, df_moving_stddev, df_bollinger_upper, df_bollinger_lower, df_bollinger_value = build_bollinger_bands(df_closingprices, n_lookback)
    # print "Moving Average\n", df_moving_avg
    # print "Moving Stddev\n", df_moving_stddev
    # print "Bollinger Upper\n", df_bollinger_upper
    # print "Bollinger Lower\n", df_bollinger_lower
    print "Bollinger Value\n", df_bollinger_value


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print """ Usage: python bollinger.py start_date end_date lookback_days

        Dates are in mm-dd-yyyy format
"""
        sys.exit(0)

    main()
