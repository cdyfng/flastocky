#!/upplication context is created and destroyed as necessary. It never moves between threads and it will not be shared between requests. As such it is the perfect place to store database connection information and other things. The internal stack object is calledsr/bin/env python
# -*- coding: utf-8 -*-
PAGESIZE = 700
WEB_TIME_OUT = 5
DM_TIME_OUT = 10
DATA_DIR = './data/air/'
DB_NAME = 'chn.db'

#API
TOT_PARAMS = 33


import urllib2
import time
import datetime
import threading
import os
#import sqlite3

from sqlalchemy.exc import IntegrityError
import Queue
from ..models_stock import Stock, Baseinfo
from .. import db
from . import stock
#from ...manage import app

INSERT_SQL = "INSERT OR IGNORE INTO `_TABLENAME_` (`id`, `stock_id`, `timestamp`, `open_price`, `yesterday_closing_price`, `now_price`, `high_price`, `low_price`, `now_buy_price`, `now_sell_price`, `volume`, `amount`, `buy_1_vol`, `buy_1_price`, `buy_2_vol`, `buy_2_price`, `buy_3_vol`, `buy_3_price`, `buy_4_vol`, `buy_4_price`, `buy_5_vol`, `buy_5_price`, `sell_1_vol`, `sell_1_price`, `sell_2_vol`, `sell_2_price`, `sell_3_vol`, `sell_3_price`, `sell_4_vol`, `sell_4_price`, `sell_5_vol`, `sell_5_price`) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS `%s` (`id` INTEGER PRIMARY KEY, `stock_id` TEXT, `timestamp` TEXT, `open_price` REAL, `yesterday_closing_price` REAL, `now_price` REAL, `high_price` REAL, `low_price` REAL, `now_buy_price` REAL, `now_sell_price` REAL, `volume` REAL, `amount` REAL, `buy_1_vol` REAL, `buy_1_price` REAL, `buy_2_vol` REAL, `buy_2_price` REAL, `buy_3_vol` REAL, `buy_3_price` REAL, `buy_4_vol` REAL, `buy_4_price` REAL, `buy_5_vol` REAL, `buy_5_price` REAL, `sell_1_vol` REAL, `sell_1_price` REAL, `sell_2_vol` REAL, `sell_2_price` REAL, `sell_3_vol` REAL, `sell_3_price` REAL, `sell_4_vol` REAL, `sell_4_price` REAL, `sell_5_vol` REAL, `sell_5_price` REAL, UNIQUE (`stock_id`, `timestamp`))"

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
    return datetime.datetime.utcnow() + datetime.timedelta(hours =+ 8)

#class sqlite_db_manager(threading.Thread):
class sqlite_db_manager():
    def __init__(self, name, io_queue, db_ctx):
        #threading.Thread.__init__(self)
        self.name = name
        self.io_queue = io_queue
        self.is_stop = False
        self.table_dict = set()
        self.db_ctx = db_ctx
        print 'self db_ctx', self.db_ctx
        print 'db_ctx', db_ctx

    def run(self):
        from sqlalchemy.exc import IntegrityError
        #global DATA_DIR
        #global DB_NAME
        #global DM_TIME_OUT
        #global CREATE_TABLE_SQL
        #global INSERT_SQL

        #file_name = DATA_DIR + '/' + DB_NAME
        #ensure_dir(file_name)
        #try:
        #    self.conn = sqlite3.connect(file_name)
        #    self.cursor = self.conn.cursor()
        #except Exception, e:
        #    print e
        #    exit()
        while (not self.is_stop) or self.io_queue.qsize() != 0:
            print 'while in'
            if self.is_stop:
                print 'Waiting items in I/O queue:', self.io_queue.qsize(), time.ctime()
            current_beijing_date = get_beijing_time().strftime('%Y-%m-%d')
            #table_name = 'table' + current_beijing_date.translate(None, '-')
            #self.table_dict.add(table_name)
            #init_table_sql = None
            #try:
            #    init_table_sql = CREATE_TABLE_SQL % table_name
            #    x = self.cursor.execute(init_table_sql)
            #except Exception, e:
            #    print e

            try:
                print self.io_queue.qsize()
                data = self.io_queue.get(True, DM_TIME_OUT)
                print 'data get ok'
            except KeyboardInterrupt, e:
                 print e
            except:
                print self.name, 'Data queue is empty. Still wait ...', time.ctime()
                continue

            print 'data save in db'
            try:
                #post_data = []

                for item in data:
                  #with app.app_context:
                    if item[1] != current_beijing_date:
                        continue
                    timestamp = ' '.join([item[1], item[2]])
                    #content = [item[0], timestamp]
                    #content.extend(list(data[item]))
                    #post_data.append(tuple(content))
                    value = list(data[item])
                    stock = Stock(stock_id = item[0],
                                  timestamp = timestamp,
                                  open_price = float(value[0]),
                                  yesterday_closing_price = float(value[1]),
                                  now_price = float(value[2]),
                                  high_price = float(value[3]),
                                  low_price = float(value[4])
                                  )
                    #print item[0], timestamp, value[0:5]
                    self.db_ctx.session.add(stock)
                #global db
                print self.db_ctx
                try:
                    self.db_ctx.session.commit()
                except IntegrityError, e:
                    print e
                    self.db_ctx.session.rollback()

                #insert = INSERT_SQL.replace('_TABLENAME_', table_name)
                #self.cursor.executemany(insert, tuple(post_data))
                #self.conn.commit()
            except Exception, e:
                print e
                print self.name, 'Error in data insertion to database!', time.ctime()
        #self.cursor.close()
        #self.conn.close()
        print self.name, 'is finished.'

    def stop(self):
        print 'Try to stop', self.name, '...'
        self.is_stop = True

    def monitor(self):
        print 'QUEUE_SIZE =', self.io_queue.qsize()
        print 'TOTAL_TABLE =', len(self.table_dict), '{',
        for name in self.table_dict:
            print name,
        print '}'

def is_trade_time():
    #return True
    current_beijing_hms = get_beijing_time().strftime('%H:%M:%S')
    if current_beijing_hms < '09:25:00':
        return False
    if current_beijing_hms > '11:35:00' and current_beijing_hms < '12:55:00':
        return False
    if current_beijing_hms > '15:05:00':
        return False
    return True


class sub_crawler(threading.Thread):
    def __init__ (self, name, code_list, io_queue):
        threading.Thread.__init__(self)
        self.name = name
        self.code_list = code_list
        self.io_queue = io_queue
        self.is_stop = False
        print 'sub %s init ' % name
    def run(self):
        global WEB_TIME_OUT
        print self.name, 'starts!'
        code_join = ','.join(self.code_list)
        while not self.is_stop:
            if not is_trade_time():
                time.sleep(5)
                continue
            good = True
            content = ''
            try:
                print 'get content'
                #sta = time.time()
                content = urllib2.urlopen('http://hq.sinajs.cn/list=' + code_join, None, WEB_TIME_OUT).read()
                #end = time.time()
                #print end - sta
                print len(content)
            except:
                print self.name, 'Network Timeout! Now try again ...', time.ctime()
                good = False
            if not good:
                continue
            data = data_parser(content)
            print 'data put'
            self.io_queue.put(data)
            print 'data put ok'
            time.sleep(30)
        print self.name, 'is finished.'
    def stop(self):
        print 'Try to stop', self.name, '...'
        self.is_stop = True


def read_code(file_name, prefix):
    code_file = open(file_name)
    ret = []
    for code in code_file:
        code = code.strip()
        ret.append(prefix + code)
    return ret

def main():
    global PAGESIZE
    code_list = Baseinfo.get_stock_ids()
    print 'Get', len(code_list), 'stock id from lists'

    io_queue = Queue.Queue()

    db_task_name = 'db_manager'
    print 'maindb',db
    db_task = sqlite_db_manager(db_task_name, io_queue, db)
    #db_task.setDaemon(True)
    #db_task.start()

    task_list = []
    cnt = 1
    for start_id in range(0, len(code_list), PAGESIZE):
        end_id = min(start_id + PAGESIZE, len(code_list))
        sub_list = code_list[start_id : end_id]
        sub_task_name = 'sub_task' + str(cnt) + '[' + str(start_id) + ',' + str(end_id - 1) + ']'
        sub_task = sub_crawler(sub_task_name, sub_list, io_queue)
        sub_task.setDaemon(True)
        cnt += 1
        task_list.append(sub_task)
        sub_task.start()

    try:
        db_task.run()
    except KeyboardInterrupt, e:
        print e

    print 'Crawler is finished!'


@stock.route('/stockidMain/s')
def aaa():
    s = Stock(stock_id='111')
    db.session.add(s)
    db.session.commit()
    #main()
    return '<h1>add ok </h1>'

def scrawler_ext():
    s = Stock(stock_id = '222')
    db.session.add(s)
    db.session.commit()
    print 'commit over'


def saveInDb():
    stocks = []
    baseinfos = Baseinfo.query.all()
    for bi in baseinfos:
        stocks.append(str(bi.stock_id))

    for start_id in range(0, len(stocks), PAGESIZE):
        end_id = min(start_id + PAGESIZE, len(stocks))
        sub_list = stocks[start_id : end_id]
        #sub_task = sub_crawler(sub_task_name, sub_list, io_queue)

        global WEB_TIME_OUT
        code_join = ','.join(sub_list)
        content = ''
        try:
            content = urllib2.urlopen(\
                'http://hq.sinajs.cn/list=' + \
                code_join, None, WEB_TIME_OUT).read()
            print len(content)
        except:
            print ''
        data = get_name_price(content)
        #print data
        for bi in baseinfos:
            stock_id = bi.stock_id
            try:
                bi.stock_name = data[stock_id][0]
                bi.now_price = data[stock_id][1]
                bi.total_value = bi.total_capital * bi.now_price
                db.session.add(bi)
            except:
                continue
        try:
            db.session.commit()
        except IntegrityError, e:
            print e
            db.session.rollback()



if __name__=='__main__':
    main()



