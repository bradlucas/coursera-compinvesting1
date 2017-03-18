#!/bin/python

import sys as sys
import datetime as dt

import pandas as pd
import numpy as np
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du


def load_orders_file(filename):
    # print "csv"
    # reader = csv.reader(open(filename, 'rU'), delimiter=',')
    # for row in reader:
    #     print row
    # print "--"

    # Using numpy to read a csv file
    ary = np.loadtxt(fname=filename, delimiter=',',
                     dtype={'names': ('year', 'month', 'day', 'symbol',
                                      'action', 'shares'),
                            'formats':
                                ('u8', 'u8', 'u8', 'S10', 'S5', 'u8')})
    return ary


def load_orders(orders_csv):
    '''Read the orders file and return as follows
    |------+-------+-----+--------+--------+--------|
    | 2011 |     1 |  05 | AAPL   | Buy    |   1500 |
    | 2011 |     1 |  07 | MSFT   | Sell   |   1500 |
    |------+-------+-----+--------+--------+--------|
                '''
    orders = load_orders_file(orders_csv)
    dates = []
    symbols = []
    for o in orders:
        date = dt.datetime(o['year'], o['month'], o['day'], 16)  # 16 is 4 pm
        dates.append(date)
        symbol = o['symbol']
        symbols.append(symbol)
    symbols = list(set(symbols))
    symbols.sort()
    dates.sort()
    return dates[0], dates[-1], symbols, orders


def load_prices(dt_start, dt_end, ls_symbols):
    '''Return two lists containing the timestamps and the prices
    Each is indexed via an 0-based id
    Prices are further put into columns indexes with the same index as ls_symbols
    '''
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    na_prices = d_data['close'].values  # use adjusted closing prices
    return ldt_timestamps, na_prices


def process(initial_balance, orders, timestamps, na_prices):
    daily_balances = []

    # Loop over the timestamps, for each day process all orders for that day and update our balance_list
    daily_order_details = []
    for idx in range(len(timestamps)):
        today = timestamps[idx]

        # order details per day is a list with slots for each symbol and a total daily amount at the end
        order_details_per_day = []
        if (idx == 0):
            # start with all zeros and the initial balance
            for i in range(len(symbols)):
                order_details_per_day.append(0)
            order_details_per_day.append(float(initial_balance))
        else:
            # start with today's based on yesterday's values
            for i in range(len(daily_order_details[idx-1])):
                order_details_per_day.append(daily_order_details[idx-1][i])
        # print "order_details_per_day" + str(order_details_per_day)

        for order in orders:
            # Do have an order for 'today'. Update the order's information in the order_details_per_day list
            if (order[0] == today.year) and (order[1] == today.month) and (order[2] == today.day):
                # |------+-------+-----+--------+--------+--------|
                # | year | month | day | symbol | action | shares |
                # |    0 |     1 |   2 | 3      | 4      |      5 |
                # |------+-------+-----+--------+--------+--------|
                # | 2011 |     1 |  05 | AAPL   | Buy    |   1500 |
                # | 2011 |     1 |  07 | MSFT   | Sell   |   1500 |
                # |------+-------+-----+--------+--------+--------|
                current_price = 0.0
                symbol = symbols.index(order[3])
                if (order[4] == 'Buy'):
                    order_details_per_day[symbol] += order[5]
                    current_price = na_prices[idx][symbol]
                    shares = order[5]
                    order_details_per_day[-1] -= shares * current_price             # we paid so we decrease
                elif (order[4] == 'Sell'):
                    order_details_per_day[symbols.index(order[3])] -= order[5]
                    current_price = na_prices[idx][symbol]
                    shares = order[5]
                    order_details_per_day[-1] += shares * current_price             # we sold so we increase

        # Save today's information in the
        daily_order_details.append(order_details_per_day)
        # print daily_order_details

        # Value of today's orders
        total = 0.0
        for i in range(len(symbols)):
            total += order_details_per_day[i] * na_prices[idx][i]
        # print "total", total
        # print "detail[-1]", order_details_per_day[-1]
        # Add to cash balance
        total += order_details_per_day[-1]

        # Day's entry
        daily_balances.append((today.year, today.month, today.day, total))

        # print "order_details_per_day" + str(order_details_per_day)
        # print "--"

    return daily_balances, daily_order_details


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print """\
Usage: python marketsim.py initial_cash orders_csv values_csv
"""
        sys.exit(0)

    # Read argumentsdef process1(initial_balance, orders, timestamps, na_prices):
    initial_balance = sys.argv[1]
    orders_csv = sys.argv[2]
    values_csv = sys.argv[3]

    # print "Arguments:"
    # print "initial_balance : " + str(initial_balance)
    # print "orders_csv      : " + orders_csv
    # print "values_csv      : " + values_csv

    # Step 1
    dt_start, dt_end, symbols, orders = load_orders(orders_csv)
    # print "dt_start : " + str(dt_start)
    # print "dt_end   : " + str(dt_end)
    # print "symbols"
    # print symbols
    # print "orders"
    # print orders
    # print "--"


    # Step 2
    ldt_timestamps, na_prices = load_prices(dt_start, dt_end, symbols)
    # print "ldt_timestamps"
    # print ldt_timestamps
    # print "na_prices"
    # print na_prices
    # print "--"
    print len(ldt_timestamps)

    # print float(initial_balance)
    # print "--"
    # Step 3
    daily_balances, daily_order_details = process(float(initial_balance), orders, ldt_timestamps, na_prices)
    # print "--"
    # print "daily_order_details"
    # for r in daily_order_details:
    #     print r
    # print "--"
    # print "daily_balances"
    # for r in daily_balances:
    #     print r

    # Output
    output_file = open(values_csv, 'wb')
    np.savetxt(output_file, daily_balances, fmt=['%d', '%d', '%d', '%.0f'], delimiter=',')

    print "The final value of the portfolio -- ", str(daily_balances[-1])

    # for v in daily_balances:
    #     print v

    # print "Done, see ", values_csv
