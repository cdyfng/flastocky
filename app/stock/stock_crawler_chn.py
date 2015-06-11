#!/upplication context is created and destroyed as necessary. It never moves between threads and it will not be shared between requests. As such it is the perfect place to store database connection information and other things. The internal stack object is calledsr/bin/env python
# -*- coding: utf-8 -*-
PAGESIZE = 700
WEB_TIME_OUT = 5
DM_TIME_OUT = 5

import urllib2
import time
import threading
from sqlalchemy.exc import IntegrityError
import Queue
from ..models_stock import Stock, Baseinfo
from .. import db
from . import stock
from .tools import *

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
        global DM_TIME_OUT
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

            data = ''
            try:
                print 'before', self.io_queue.qsize()
                #data = self.io_queue.get(True, DM_TIME_OUT)
                data = self.io_queue.get(True, 5)
                #print 'data get ok' ,  DM_TIME_OUT
                print 'after', self.io_queue.qsize()
            except KeyboardInterrupt, e:
                 print e
            except Exception, e:
                print e
                print self.name, 'Data queue is empty. Still wait ...', time.ctime()
                continue

            print 'data save in db',time.ctime()

            #continue
            try:
                #post_data = []
                timestamp = ''

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
                print self.db_ctx, timestamp
                try:
                    self.db_ctx.session.commit()
                except IntegrityError, e:
                    print e
                    self.db_ctx.session.rollback()
                print time.ctime()

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
            t = 60 if self.io_queue.qsize() <= 4 else 120
            time.sleep(t)
        print self.name, 'is finished.'
    def stop(self):
        print 'Try to stop', self.name, '...'
        self.is_stop = True


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


