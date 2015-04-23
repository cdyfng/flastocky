from datetime import datetime
from . import db


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


    @staticmethod
    def bg_running(self):
        '''get data from sina and save in db'''
        pass


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

    def __repr__(self):
        return '<Baseinfo %r %r>' % (self.stock_id, self.timestamp)


#CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS `%s` \
    #(`id` INTEGER PRIMARY KEY, `stock_id` TEXT, \
    #`timestamp` TEXT, `open_price` REAL, \
    #`yesterday_closing_price` REAL, `now_price` REAL, \
    #`high_price` REAL, `low_price` REAL, `now_buy_price` REAL, \
    #`now_sell_price` REAL, `volume` REAL, `amount` REAL, \
    #`buy_1_vol` REAL, `buy_1_price` REAL, \
    #`buy_2_vol` REAL, `buy_2_price` REAL, \
    #`buy_3_vol` REAL, `buy_3_price` REAL, \
    #`buy_4_vol` REAL, `buy_4_price` REAL, \
    #`buy_5_vol` REAL, `buy_5_price` REAL, \
    #`sell_1_vol` REAL, `sell_1_price` REAL, `sell_2_vol` REAL, `sell_2_price` REAL, `sell_3_vol` REAL, `sell_3_price` REAL, `sell_4_vol` REAL, `sell_4_price` REAL, \
    #`sell_5_vol` REAL, `sell_5_price` REAL, \
    #UNIQUE (`stock_id`, `timestamp`))"

#CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS `%s` \
    #(`id` INTEGER PRIMARY KEY, `stock_id` TEXT, \
    #`timestamp` TEXT, `open_price` REAL, \
    #`yesterday_closing_price` REAL, `now_price` REAL, \
    #`high_price` REAL, `low_price` REAL, `now_buy_price` REAL, \
    #`now_sell_price` REAL, `volume` REAL, `amount` REAL, \
    #`buy_1_vol` REAL, `buy_1_price` REAL, \
    #`buy_2_vol` REAL, `buy_2_price` REAL, \
    #`buy_3_vol` REAL, `buy_3_price` REAL, \
    #`buy_4_vol` REAL, `buy_4_price` REAL, \
    #`buy_5_vol` REAL, `buy_5_price` REAL, \
    #`sell_1_vol` REAL, `sell_1_price` REAL, `sell_2_vol` REAL, `sell_2_price` REAL, `sell_3_vol` REAL, `sell_3_price` REAL, `sell_4_vol` REAL, `sell_4_price` REAL, \
    #`sell_5_vol` REAL, `sell_5_price` REAL, \
    #UNIQUE (`stock_id`, `timestamp`))"
