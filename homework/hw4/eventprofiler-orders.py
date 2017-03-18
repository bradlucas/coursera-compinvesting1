#!/bin/python

import pandas as pd
import numpy as np
# import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
# import QSTK.qstkutil.tsutil as tsu
# import QSTK.qstkstudy.EventProfiler as ep
import sys

# @see http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_2


def sym_down_amount(ls_symbols, d_data, event_amount):
    '''Find events where the actual close of the stock price
drops below an amount'''
    df_actual_close = d_data['actual_close']
    # ts_market = df_actual_close['SPY']

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actual_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_actual_close.index

    # create orders dataframe
    df_columns = ['year', 'month', 'day', 'symbol', 'order', 'shares']
    df_orders = pd.DataFrame(columns=df_columns)

    event_count = 0
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_actual_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_actual_close[s_sym].ix[ldt_timestamps[i - 1]]
            # f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            # f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            # f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            # f_marketreturn_today = (f_marketprice_today/f_marketprice_yest)-1

            # Homework 2
            # The event is defined as when the actual close of the stock price
            # drops below $5.00,
            # price[t-1] >= 5.0
            # price[t] < 5.0
            # an event has occurred on date t.

            # Note that just because the price is below 5 it is not an event
            # for every day that
            # it is below 5, only on the day it first drops below 5.

            if f_symprice_today < event_amount and f_symprice_yest >= event_amount:
                # Buy
                row = pd.DataFrame([{
                    'year': ldt_timestamps[i].year,
                    'month': ldt_timestamps[i].month,
                    'day': ldt_timestamps[i].day,
                    'symbol': s_sym,
                    'order': 'Buy',
                    'shares': 100}])
                df_orders = df_orders.append(row)
                sell_date_idx = i + 5
                if sell_date_idx >= len(ldt_timestamps):
                    sell_date_idx = len(ldt_timestamps) - 1
                row = pd.DataFrame([{
                    'year': ldt_timestamps[sell_date_idx].year,
                    'month': ldt_timestamps[sell_date_idx].month,
                    'day': ldt_timestamps[sell_date_idx].day,
                    'symbol': s_sym,
                    'order': 'Sell',
                    'shares': 100}])
                df_orders = df_orders.append(row)
                event_count += 1
    print "Events    : " + str(event_count)
    return df_orders


def run(dt_start, dt_end, s_list, find_function, event_amount):
    print "-----------------------------------------------------------"
    print "Start date: " + str(dt_start)
    print "End date  : " + str(dt_end)
    print "Symbols   : " + s_list
    print "Function  : " + find_function.__doc__
    print "Event Amt : " + str(event_amount)

    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(s_list)
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_orders = find_function(ls_symbols, d_data, event_amount)
    return df_orders


if __name__ == '__main__':
    if len(sys.argv) != 4:
            print """
Usage: python eventprofiler_output.py dt_start dt_end event_amount

Date formats in mm-dd-yyyy
Event amount should be in 0.0 format

"""
            sys.exit(0)

    # print sys.argv[1]
    # print sys.argv[2]
    # print sys.argv[3]

    dt_start = dt.datetime.strptime(sys.argv[1], '%m-%d-%Y')
    dt_end = dt.datetime.strptime(sys.argv[2], '%m-%d-%Y')
    event_amount = float(sys.argv[3])

    # print dt_start
    # print dt_end
    # print event_amount

    output_file = 'orders-' + str(event_amount).replace('.', '-') + ".csv"
    # print output_file

    # dt_start = dt.datetime(2008, 1, 1)
    # dt_end = dt.datetime(2009, 12, 31)

    # Starting cash: $50,000
    # Start date: 1 January 2008
    # End date: 31 December 2009
    # When an event occurs, buy 100 shares of the equity on that day.
    # Sell automatically 5 trading days later.

    df_orders = run(dt_start, dt_end, 'sp5002012', sym_down_amount, event_amount)

    df_columns = ['year', 'month', 'day', 'symbol', 'order', 'shares']
    df_orders.to_csv(
        output_file,
        header=None,
        index=None,
        columns=df_columns,
        float_format='%02.f')
