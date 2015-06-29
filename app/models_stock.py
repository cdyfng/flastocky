from datetime import datetime
from . import db
from ystockquote import get_historical_prices
from sqlalchemy.exc import IntegrityError
import time
#from app.stock import data_parser
#from app.stock.stock_crawler_chn import data_parser
#from app.exceptions import ValidationError
from app.stock.tools import *
from app.stock.reminder import *
import urllib2

red_color = '\033[;31;40m %s \033[0m'
green_color = '\033[;32;40m %s \033[0m'

class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(10))
    timestamp = db.Column(db.String(20))
    open_price = db.Column(db.Float)
    yesterday_closing_price = db.Column(db.Float)
    now_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    __table_args__ = (db.UniqueConstraint('stock_id', 'timestamp'),)

    def __repr__(self):
        return '<Stock %r %r>' % (self.stock_id, self.timestamp)

    def to_string(self):
        return '%s %s %f %f %f %f %f' % (self.stock_id, self.timestamp, \
                self.open_price, self.yesterday_closing_price, \
                self.now_price, self.high_price, self.low_price)

    @staticmethod
    def bg_running(self):
        '''get data from sina and save in db'''
        pass

    @staticmethod
    def on_change_price(target, value, oldvalue, initiator):
        #print 'value %f, oldvalue %f' % (value, oldvalue)
        #print target.stock_id
        #print macro_arg
        try:
            Reminder.run(target, value)
        except Exception as e:
            print e

db.event.listen(Stock.now_price, 'set', Stock.on_change_price)


class Baseinfo(db.Model):
    __tablename__ = 'baseinfo'
    #id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(10), primary_key=True)
    stock_name = db.Column(db.UnicodeText)
    timestamp = db.Column(db.String(20), default=datetime.utcnow)
    stock_type = db.Column(db.Text)
    total_capital = db.Column(db.Float)
    total_value = db.Column(db.Float)
    pe_ratio_static = db.Column(db.Float)
    pe_ratio_dynamic = db.Column(db.Float)
    pb = db.Column(db.Float)
    income = db.Column(db.Float)
    industry = db.Column(db.UnicodeText)
    main_busyness = db.Column(db.UnicodeText)
    concept = db.Column(db.UnicodeText)
    now_price = db.Column(db.Float)
    volumn = db.Column(db.Float)
    __table_args__ = (\
        db.UniqueConstraint('stock_id', 'pe_ratio_static', \
                            'pe_ratio_dynamic', 'pb'),)
    history = db.relationship('StockHistory', backref='baseinfo',\
                                    lazy='dynamic')

    def __repr__(self):
        return '<Baseinfo %r %r>' % (self.stock_id, self.timestamp)

    @staticmethod
    def get_stock_ids():
        stocks = []
        baseinfos = Baseinfo.query.all()
        for bi in baseinfos:
            stocks.append(str(bi.stock_id))
        return stocks

    @staticmethod
    def get_id_name_dict():
        d = {}
        baseinfos = Baseinfo.query.all()
        for bi in baseinfos:
            d[bi.stock_id] = bi.stock_name
        return d


class StockHistory(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(10), \
                         db.ForeignKey('baseinfo.stock_id'))
    date = db.Column(db.String(20))
    open = db.Column(db.Float)
    close = db.Column(db.Float)
    adjclose = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    volume = db.Column(db.Float)
    __table_args__ = (\
        db.UniqueConstraint('stock_id', 'date'),)

    def __repr__(self):
        return '<stockhistory %r %r>' % (self.stock_id, self.date)

    @staticmethod
    def init_db_from_yahoo(start='2010-01-01', \
                           end=(str(datetime.now()))[0:10]):
        #print start
        #print end
        #hp = get_historical_prices('600999.SS', start, end)
        stocks = Baseinfo.get_stock_ids()
        all_start = time.time()
        print len(stocks)
        for stock in stocks:
            sh = StockHistory.query.filter_by(stock_id = stock)\
                .filter_by(date='2015-06-08').first()
            if sh is not None:
                print '%s already in' % stock
                continue
            time.sleep(1)
            tick_start = time.time()
            postfix = '.ss' if stock[0:2] == 'sh' else '.sz'
            stock_yahoo_style = stock[2:] + postfix
            try:
                print stock_yahoo_style, start, end

                hp = get_historical_prices(stock_yahoo_style, start, end)
                #print hp
                now = time.time()
                print "%s, %d cost %f//%d " \
                    %(stock, len(hp), now-tick_start, now-all_start)
                for item in hp:
                    stockhistory = StockHistory(
                    stock_id = stock,
                    date = item,
                    open = float(hp[item]['Open']),
                    close = float(hp[item]['Close']),
                    high = float(hp[item]['High']),
                    low = float(hp[item]['Low']),
                    adjclose = float(hp[item]['Adj Close']),
                    volume = float(hp[item]['Volume']),
                    )
                    db.session.add(stockhistory)
                db.session.commit()

            except IntegrityError, e:
                print e
                db.session.rollback()
            except Exception as  e:
                print e
            #time.sleep(1)

    @staticmethod
    def daily_sina_reflash():
        PAGESIZE = 700
        WEB_TIME_OUT = 5
        stocks = Baseinfo.get_stock_ids()
        all_start = time.time()
        #print len(stocks)
        for start_id in range(0, len(stocks), PAGESIZE):
            end_id = min(start_id + PAGESIZE, len(stocks))
            sub_list = stocks[start_id : end_id]
            #sub_task = sub_crawler(sub_task_name, sub_list, io_queue)

            code_join = ','.join(sub_list)
            content = ''
            #print code_join
            try:
                content = urllib2.urlopen(\
                    'http://hq.sinajs.cn/list=' + \
                    code_join, None, WEB_TIME_OUT).read()
                print len(content)
            except Exception as e:
                print 'sina get except'
                print e

            data = data_parser(content)
            print len(data)
            for item in data:
                sh = StockHistory(
                    stock_id = item[0],
                    date = item[1],
                    open = float(data[item][0]),
                    close = float(data[item][2]),
                    high = float(data[item][3]),
                    low = float(data[item][4]),
                    adjclose = float(data[item][1]),
                    volume = float(data[item][7]),
                    )
                db.session.add(sh)
            db.session.commit()
                #print sh.stock_id, sh.date, sh.open, sh.close, sh.high, \
                #    sh.low, sh.adjclose, sh.volume
            time.sleep(1)

            #except IntegrityError, e:
            #    print e
            #    db.session.rollback()
            #except Exception as  e:
            #    print e
            #time.sleep(1)

    def sim_trading(self, days):
        shs = StockHistory.query\
            .filter_by(stock_id=self.stock_id)\
            .order_by(StockHistory.date.desc())\
            .limit(int(days))\
            .all()
        shs.reverse()
        low_last_3 = []
        high_last_3 = []
        buy_sell = 0
        threshold_percent = 0.0
        buy_price = 0.0
        sell_price = 0.0
        init_price = 0.0
        net_worth = 1.0
        for sh in shs:
            if sh.volume == 0: continue
            if len(low_last_3)>=3:
                if buy_sell == 0:
                    thl = min(low_last_3) * (1-threshold_percent)
                    if sh.low < thl:
                        buy_sell = 1
                        buy_price = thl
                        if init_price == 0.0: init_price = buy_price
                        print 'buy %s @ %.2f' % (sh.date,buy_price)
                elif buy_sell == 1:
                    thh = max(high_last_3) * (1 + threshold_percent)
                    if sh.high > thh:
                        buy_sell = 0
                        sell_price = thh
                        print 'sell %s @ %.2f' % (sh.date,sell_price)
                        cur_profit = (sell_price-buy_price)/buy_price
                        color = red_color if cur_profit > 0.0 else green_color
                        print color % (cur_profit)
                        net_worth = net_worth * (1 + cur_profit)
                        market_worth = sh.close/init_price
                        print "profit %.2f vs %.2f"%(net_worth, market_worth)

            if len(low_last_3)>=3:low_last_3.remove(low_last_3[0])
            low_last_3.append(sh.low)
            if len(high_last_3)>=3:high_last_3.remove(high_last_3[0])
            high_last_3.append(sh.high)
            print sh.date, sh.close, sh.low, sh.high, sh.volume, \
                (sh.high -sh.low)/sh.adjclose* 100
        print '\n', shs[0].date, shs[0].open
        print  shs[days-1].date, shs[days-1].open
        return shs


class RealtimeInfo(db.Model):
    __tablename__ = 'realtimeinfo'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(10), \
                         db.ForeignKey('baseinfo.stock_id'))
    timestamp = db.Column(db.String(20), default=datetime.now)
    riseTop = db.Column(db.Boolean, default=False)
    riseTopOpen = db.Column(db.Boolean, default=False)
    fallBottom = db.Column(db.Boolean, default=False)
    fallBottomOpen = db.Column(db.Boolean, default=False)
    extra1 = db.Column(db.Boolean, default=False)
    extra2 = db.Column(db.Boolean, default=False)
    extra3 = db.Column(db.Boolean, default=False)
    __table_args__ = (\
        db.UniqueConstraint('stock_id', 'timestamp'),)

    def __repr__(self):
        return '<realtimeinfo %r %r>' % (self.stock_id, self.timestamp)

    @staticmethod
    def init_daily(today=(str(datetime.now()))[0:10]):
        '''
        return today's recoder when initial
        '''
        return RealtimeInfo.query.filter\
            (RealtimeInfo.timestamp.like(today + '%')).all()


