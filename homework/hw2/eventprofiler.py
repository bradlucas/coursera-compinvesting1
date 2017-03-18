#!/bin/python

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


# @see http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_9
#
# Event definition: (daily_return($SPX) >= 0.02) and (daily_return(equity) < -0.03)
# Event in English: The S&P 500 index gains more than 2% and the equity drops more then 3%.
def spy_up_2_sym_down_3(ls_symbols, d_data):
    '''The S&P 500 index gains more than 2% and the equity drops more then 3%.'''
    df_actual_close = d_data['close']
    ts_market = df_actual_close['SPY']
    event_count = 0

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actual_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_actual_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_actual_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_actual_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1

            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol is down more then 3%
            # while the market is up more then 2%
            if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                event_count += 1

    return event_count, df_events

# @see http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_2

def sym_down_5(ls_symbols, d_data):
    '''Find events where the actual close of the stock price drops below $5.00'''
    df_actual_close = d_data['actual_close']
    ts_market = df_actual_close['SPY']
    event_count = 0

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actual_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_actual_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_actual_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_actual_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Homework 2
            # The event is defined as when the actual close of the stock price drops below $5.00,
            # price[t-1] >= 5.0
            # price[t] < 5.0
            # an event has occurred on date t.
            # Note that just because the price is below 5 it is not an event for every day that it is below 5, only on the day it first drops below 5.

            if f_symprice_today<5.0 and f_symprice_yest >= 5.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                event_count += 1;

    return event_count, df_events


def run(dt_start, dt_end, s_list, find_function, filename):
    print "-----------------------------------------------------------"
    print "Start date: " + str(dt_start)
    print "End date  : " + str(dt_end)
    print "Symbols   : " + s_list
    print "Filename  : " + filename
    print "Function  : " + find_function.__doc__

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

    event_count, df_events = find_function(ls_symbols, d_data)
    print "Events    : " + str(event_count)
    s_filename = filename
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20, s_filename=s_filename, b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')
    print "-----------------------------------------------------------"


if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)

    # Original tutorial
    # run(dt_start, dt_end, 'sp5002012', spy_up_2_sym_down_3, 'spy_up_2_syn_down_3-sp500-2012.pdf')
    # run(dt_start, dt_end, 'sp5002008', spy_up_2_sym_down_3, 'spy_up_2_syn_down_3-sp500-2008.pdf')

    # These result counts are from the PDF view which will be fewer due to the data window
    # For the $5.0 event with S&P500 in 2012, we find 176 events. Date Range = 1st Jan,2008 to 31st Dec, 2009.
    # For the $5.0 event with S&P500 in 2008, we find 326 events. Date Range = 1st Jan,2008 to 31st Dec, 2009.
    run(dt_start, dt_end, 'sp5002008', sym_down_5, 'sym_down_5-sp500-2008.pdf')
    run(dt_start, dt_end, 'sp5002012', sym_down_5, 'sym_down_5-sp500-2012.pdf')


    # My results. Event count is the actual number. PDF view matches the above
    # -----------------------------------------------------------
    # Start date: 2008-01-01 00:00:00
    # End date  : 2009-12-31 00:00:00
    # Symbols   : sp5002008
    # Filename  : sym_down_5-sp500-2008.pdf
    # Function  : Find events where the actual close of the stock price drops below $5.00
    # Events    : 331
    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # Start date: 2008-01-01 00:00:00
    # End date  : 2009-12-31 00:00:00
    # Symbols   : sp5002012
    # Filename  : sym_down_5-sp500-2012.pdf
    # Function  : Find events where the actual close of the stock price drops below $5.00
    # Events    : 180
    # -----------------------------------------------------------

