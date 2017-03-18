#!/bin/python

import copy
import datetime as dt
import sys

import pandas as pd
import numpy as np

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

# Build bollinger values for SP5002012 as well as $SPX
# build data frame for symbol


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
    return d_data, df_closingprices


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


def build_symbol_list(s_list, index_name):
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(s_list)
    ls_symbols.append('SPY')
    return ls_symbols


def event_study(df_bollinger_value):

    # Bollinger value for the equity today <= -2.0
    # Bollinger value for the equity yesterday >= -2.0
    # Bollinger value for SPY today >= 1.0
    ldt_timestamps = df_bollinger_value.index
    ls_symbols = df_bollinger_value.columns
    # print "ls_symbols", ls_symbols

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_bollinger_value)
    df_events = df_events * np.NAN

    event_count = 0
    for s_sym in ls_symbols:
        # ignore SPY
        if s_sym != 'SPY':
            for i in range(1, len(ldt_timestamps)):
                bollinger_value_today = df_bollinger_value[s_sym].ix[ldt_timestamps[i]]
                bollinger_value_yesterday = df_bollinger_value[s_sym].ix[ldt_timestamps[i-1]]
                bollinger_value_today_spy = df_bollinger_value['SPY'].ix[ldt_timestamps[i]]

                if bollinger_value_today <= -2.0 and bollinger_value_yesterday >= -2.0 and bollinger_value_today_spy >= 1.0:
                    df_events[s_sym].ix[ldt_timestamps[i]] = 1
                    event_count += 1

    return event_count, df_events


if __name__ == '__main__':
    dt_start_param = sys.argv[1]
    dt_start = dt.datetime.strptime(dt_start_param, '%m-%d-%Y')
    dt_end_param = sys.argv[2]
    dt_end = dt.datetime.strptime(dt_end_param, '%m-%d-%Y')
    n_lookback = int(sys.argv[3])

    # dt_start = dt.datetime.strptime('01-01-2008', '%m-%d-%Y')
    # dt_end = dt.datetime.strptime('12-31-2009', '%m-%d-%Y')
    # n_lookback = 20

    symbol_list = 'sp5002012'
    index = '$SPX'
    ls_symbols = build_symbol_list(symbol_list, index)
    # print ls_symbols

    d_data, df_closingprices = fetch_close_prices(dt_start, dt_end, ls_symbols)

    df_moving_avg, df_moving_stddev, df_bollinger_upper, df_bollinger_lower, df_bollinger_value = build_bollinger_bands(df_closingprices, n_lookback)

    event_count, df_events = event_study(df_bollinger_value)

    print "Events    : " + str(event_count)
    s_filename = dt_start_param + "-" + dt_end_param + "-" + symbol_list + "-" + index + "-bollinger-events.pdf"

    # eventprofiler depends on d_data['close']
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20, s_filename=s_filename, b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')

