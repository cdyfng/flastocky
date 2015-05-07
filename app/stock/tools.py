#!/upplication context is created and destroyed as necessary. It never moves between threads and it will not be shared between requests. As such it is the perfect place to store database connection information and other things. The internal stack object is calledsr/bin/env python
# -*- coding: utf-8 -*-
PAGESIZE = 700
WEB_TIME_OUT = 5
DM_TIME_OUT = 10
#API
TOT_PARAMS = 33


from datetime import datetime,timedelta
import os, time

def data_parser(data):
    """
    return a dict:
    key is a tuple (stock_id, date, time)
    value is a tuple contains parameters in the following order
    (
        open_price, yesterday_closing_price,
        now_price, high_price, low_price,
        now_buy_price, now_sell_price, #same as buy_1_price and sell_1_price
        volume, amount,
        buy_1_vol, buy_1_price,
        buy_2_vol, buy_2_price,
        buy_3_vol, buy_3_price,
        buy_4_vol, buy_4_price,
        buy_5_vol, buy_5_price,
        sell_1_vol, sell_1_price,
        sell_2_vol, sell_2_price,
        sell_3_vol, sell_3_price,
        sell_4_vol, sell_4_price,
        sell_5_vol, sell_5_price
    )
    """
    global TOT_PARAMS
    ret = dict()
    lines = data.split('\n')
    for line in lines:

        eq_pos = line.find('=')
        if eq_pos == -1:
            continue

        params_seg = line[eq_pos + 2:-1]
        params = params_seg.split(',')
        if len(params) != TOT_PARAMS:
            continue

        stock_id_seg = line[:eq_pos]
        stock_id = stock_id_seg[stock_id_seg.rfind('_') + 1:]
        date = params[30]
        time = params[31]
        #params[32] is nothing

        key = (stock_id, date, time)

        value = tuple(params[1:30])

        ret[key] = value
    return ret


def get_name_price(data):
    """
    return name and price of stocks:
    data in is the following order
    (
        open_price, yesterday_closing_price,
        now_price, high_price, low_price,
        now_buy_price, now_sell_price, #same as buy_1_price and sell_1_price
        volume, amount,
        buy_1_vol, buy_1_price,
        buy_2_vol, buy_2_price,
        buy_3_vol, buy_3_price,
        buy_4_vol, buy_4_price,
        buy_5_vol, buy_5_price,
        sell_1_vol, sell_1_price,
        sell_2_vol, sell_2_price,
        sell_3_vol, sell_3_price,
        sell_4_vol, sell_4_price,
        sell_5_vol, sell_5_price
    )
    """
    global TOT_PARAMS
    ret = dict()
    lines = data.split('\n')
    for line in lines:

        eq_pos = line.find('=')
        if eq_pos == -1:
            continue

        params_seg = line[eq_pos + 2:-1]
        params = params_seg.split(',')
        if len(params) != TOT_PARAMS:
            continue

        stock_id_seg = line[:eq_pos]
        stock_id = stock_id_seg[stock_id_seg.rfind('_') + 1:]

        #date = params[30]
        #time = params[31]
        #params[32] is nothing

        #key = (stock_id, date, time)
        key = stock_id

        #value = tuple(params[1:30])
        value = tuple([params[0].decode('gbk'), \
                       float(params[3])])

        ret[key] = value
    return ret


def ensure_dir(file_name):
    root_dir = os.path.dirname(file_name)
    if root_dir == '':
        root_dir == '.'
    if not os.path.exists(root_dir):
        ensure_dir(root_dir)
        os.makedirs(root_dir)


def get_beijing_time():
    return datetime.utcnow() + timedelta(hours =+ 8)


def is_trade_time():
    today = int(time.strftime("%w"))
    if today ==0 or today == 6: return False
    #return True
    current_beijing_hms = get_beijing_time().strftime('%H:%M:%S')
    if current_beijing_hms < '09:25:00':
        return False
    if current_beijing_hms > '11:35:00' and current_beijing_hms < '12:55:00':
        return False
    if current_beijing_hms > '15:05:00':
        return False
    return True


def read_code(file_name, prefix):
    code_file = open(file_name)
    ret = []
    for code in code_file:
        code = code.strip()
        ret.append(prefix + code)
    return ret


if __name__=='__main__':
    pass



