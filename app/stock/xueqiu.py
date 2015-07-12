#!/usr/bin/env python
#coding=utf-8

import requests, time, math, os
from json import JSONDecoder
from ..models_stock import Baseinfo
from .. import db
#from .tools import stock_base_info
from .stock_notify import stock_base_info
from sqlalchemy.exc import IntegrityError
import logging
logging.basicConfig(level=logging.DEBUG,\
    format='%(asctime)s|%(filename)s|%(funcName)s|line:%(lineno)d|%(levelname)s|%(message)s',
    datefmt='%Y-%m-%d %X',
    filename=os.path.dirname(os.path.abspath(__file__)) +'/xueqiu_daily.log'
    )

ITEM_PER_PAGE = 90

s = requests.Session()
s.headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    }
#r = s.get('http://xueqiu.com', timeout=5, verify=False)
def get_index_page():
    r = s.get('http://www.xueqiu.com', \
              timeout=5, verify=False)
    return r

def login():
    username = os.environ.get('XUEQIU_USERNAME')
    password = os.environ.get('XUEQIU_PASSWORDHASH')
    params = {'username':'',
              'areacode':'86',
              'telephone':username,
              'remember_me':'0',
              'password':password,
              }
    url = 'http://xueqiu.com/user/login'
    '''s.headers = {
        'Host': 'xueqiu.com',
        'Connection': 'keep-alive',
        'Origin': 'http://xueqiu.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
        'cache-control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://xueqiu.com/1267351120',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }'''
    r = s.post(url, data=params)
    return r

def get_stock_list(page):
    '''run login() before get_stock_list()'''
    url = 'http://xueqiu.com/stock/cata/stocklist.json?page=%s&size=%d&order=desc&orderby=percent&type=11%%2C12&_=1431054522457'\
        % (page, ITEM_PER_PAGE)
    '''s.headers ={
        'Host': 'xueqiu.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'cache-control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
        'Referer': 'http://xueqiu.com/hq',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        #'Cookie': 'xq_a_token=39d6304bf28af3d0e6424795e0d0b210c91568c6; xq_r_token=365b51d13be704cbff32038faffa8dfef2a1914c; __utmt=1; __utma=1.1838815250.1431052045.1431052045.1431054429.2; __utmb=1.2.10.1431054429; __utmc=1; __utmz=1.1431052045.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_1db88642e346389874251b5a1eded6e3=1431052042; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1431054441',
        #'Cookie': 'xq_a_token=857c238b66901ed785a9509b6496ff48674e50ff; xqat=857c238b66901ed785a9509b6496ff48674e50ff; xq_r_token=fd7ef153ff7f0501a284b439821e5ef5782fd805; xq_is_login=1; bid=56fbadc9662859fa2c254f80db9f27da_i9iexwu5; snbim_minify=true; __utmt=1; __utma=1.1838815250.1431052045.1431310354.1431340460.8; __utmb=1.2.10.1431340460; __utmc=1; __utmz=1.1431052045.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_1db88642e346389874251b5a1eded6e3=1431052042,1431259334; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1431340489d=56fbadc9662859fa2c254f80db9f27da_i9iexwu5; snbim_minify=true; xq_a_token=42e30b0295e575f2e8edaeb2c1704396bf1fd30d; xq_r_token=c7ec305e80b3fd0943f88fa00d5496132699002a; xq_token_expire=Fri%20Jun%2005%202015%2020%3A54%3A45%20GMT%2B0800%20(CST); xq_is_login=1; __utmt=1; __utma=1.1838815250.1431052045.1431345078.1431348886.10; __utmb=1.34.9.1431349354439; __utmc=1; __utmz=1.1431345078.9.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=sh900906; Hm_lvt_1db88642e346389874251b5a1eded6e3=1431052042,1431259334,1431345078; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1431349817'
        'Cookie': 'bid=56fbadc9662859fa2c254f80db9f27da_i9iexwu5; snbim_minify=true; xq_a_token=42e30b0295e575f2e8edaeb2c1704396bf1fd30d; xq_r_token=c7ec305e80b3fd0943f88fa00d5496132699002a; xq_token_expire=Fri%20Jun%2005%202015%2020%3A54%3A45%20GMT%2B0800%20(CST); xq_is_login=1; __utmt=1; __utma=1.1838815250.1431052045.1431345078.1431348886.10; __utmb=1.34.9.1431349354439; __utmc=1; __utmz=1.1431345078.9.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=sh900906; Hm_lvt_1db88642e346389874251b5a1eded6e3=1431052042,1431259334,1431345078; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1431349817'
    }'''
    r = s.get(url)
    #print r.content
    print len(r.content)
    try:
        return JSONDecoder().decode(r.content)
    except:
        print 'error'
        print r.content['error_description']
        logging.error('%s', str(r.content['error_description']))

def sh_sz_stock_info():
    '''return list ,every item as follow:
        {u'volume': u'17340', u'high': u'0.546',
         u'code': u'900950', u'name': u'\u65b0\u57ceB\u80a1',
         u'symbol': u'SH900950', u'high52w': u'0.546',
         u'percent': u'10.08', u'current': u'0.546',
         u'hasexist': u'false', u'amount': u'9468.0',
         u'low52w': u'0.438', u'low': u'0.546',
         u'pettm': u'4.46', u'change': u'0.05',
         u'marketcapital': u'8.698802112E8'}
        '''
    d = get_stock_list(str(1))
    page = math.ceil(d['count']['count']/ITEM_PER_PAGE)
    #print str(i), time.time()-start
    l = []
    for i in range(1,int(page)+1):
    #for i in range(1, 2):
        l =  l + get_stock_list(str(i))['stocks']

        #print str(i), time.time()-start
        time.sleep(1)
    return l


def daily_update_baseinfo():
    l = sh_sz_stock_info()
    stocks_now = []
    for item in l:
        #if item['symbol'].lower()[0:3] in ['pre','sh1','sh0','sh9',]:
        #    continue
        if item['symbol'].lower()[0:4] in ['sz39',]:
            continue
        if item['symbol'].lower()[0:3] in ['sh6','sz0','sz3',]:
            #取得雪球沪深b股外的所有股票代码
            stocks_now.append(item['symbol'].lower())
    #取得数据库中已有的股票代码
    stocks_pre = Baseinfo.get_stock_ids()
    #得到数据库中未保存的股票代码
    stocks = list(set(stocks_now) - set(stocks_pre))
    start_time = time.time()
    #stocks = [u'sh603030',]
    print len(stocks)
    for stock in stocks:
        #新股票代码取基本面信息存入数据库
        #print type(stock)
        stock = str(stock)
        #print type(stock)
        try:
            each_start_time = time.time()
            seprator = '-' * 40
            #print stock
            info = stock_base_info(stock[2:])
            #print info
            #strInfo = '%s %s %s %.2f(tl) \
            #    %.2f(p) %.2f(rf) %.2f(d) \
            #    %.2f(s) %.2f(pb) %.2f \n%s \
            #    |%s \n%s \n%s\n' \
            #    %(info['code'], \
            #      'none', \
            #      info['type'], info['total_capital']* 1.0, \
            #      1.0, 1.0, \
            #   info['pe_ratio_static'], info['pe_ratio_dynamic'], \
            #      info['pb'], info['income'], \
            #   info['industry'].encode('utf-8'), \
            #      info['main_busyness'].encode('utf-8'),
            #   info['concept'].encode('utf-8'), seprator)
            base_info = \
                Baseinfo(stock_id=stock, stock_type=info['type'],\
                         total_capital=info['total_capital'],\
                         pe_ratio_static=info['pe_ratio_static'],\
                         pe_ratio_dynamic=info['pe_ratio_dynamic'],\
                         pb=info['pb'],income=info['income'],\
                         industry=info['industry'],\
                         main_busyness=info['main_busyness'],\
                         concept=info['concept'])
            strInfo =  info['code'] + info['industry'] + \
                info['concept'] + info['main_busyness']

            try:
                db.session.add(base_info)
                db.session.commit()
            except IntegrityError, e:
                db.session.rollback()

            print '本次抓取时间:%.2f, 总耗时%d' \
                % (time.time() - each_start_time, time.time() - start_time)
            logging.info('%s', strInfo)
            #print '---------------------------------------------------'
            time.sleep(1)

        except Exception as e:
            info = {}
            print stock
            print e
            logging.error('%s', e)
        #log
        #print stock

    #baseinfo更新市盈率和股价以及市值等信息


    print 'now:',len(stocks_now),'db:',len(stocks_pre),'add:',len(stocks)
    print 'update price, market value, stock_name'
    for item in l:
        bi = Baseinfo.query\
            .filter_by(stock_id=item['symbol'].lower()).first()
        if bi is not None:
            bi.stock_name = item['name']
            bi.now_price = float(item['current'])
            bi.total_value = float(item['marketcapital'])/1000000000
            bi.low52w = float(item['low52w'])
            bi.high52w = float(item['high52w'])
            try:
                db.session.add(bi)
                db.session.commit()
            except IntegrityError, e:
                db.session.rollback()
                logging.error('%s', e)



if __name__ == '__main__':
    start = time.time()
    daily_update_baseinfo()
    #d = get_stock_list(str(1))
    #page = math.ceil(d['count']['count']/ITEM_PER_PAGE)
    #print str(i), time.time()-start
    #l = []
    #for i in range(1,int(page)+1):
    #for i in range(1, 5):
    #    l =  l + get_stock_list(str(i))['stocks']

    #    print str(i), time.time()-start
    #    time.sleep(1)

    #print l[1]
    #Check stocks
    #stocks_now = []
    #for item in l:
    #    stocks_now.append(item['symbol'].lower())
    #print stocks_now
    #print len(stocks_now)

    #stocks_pre = []
    #stocks = list(set(stocks_now) - set(stocks_pre))
    #print len(stocks)
    #print stocks[0]
    #print page
