from datetime import datetime
from . import db
from sqlalchemy.exc import IntegrityError
import time

red_color = '\033[;31;40m %s \033[0m'
green_color = '\033[;32;40m %s \033[0m'

class BacktestingLog(db.Model):
    __tablename__ = 'backtest'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    timestamp = db.Column(db.String(20), default=datetime.now)
    strategy_name = db.Column(db.String(10))
    parameters = db.Column(db.String(40))
    parameters_ext = db.Column(db.String(40))
    name = db.Column(db.UnicodeText)
    #__table_args__ = (db.UniqueConstraint('stock_id', 'timestamp'),)

    def __repr__(self):
        return '<BacktestingLog %r %r %r>' % (self.code, self.timestamp, self.name)

    def to_string(self):
        return '%s %s %s %s %s  %s' % (self.code, self.timestamp, \
                self.strategy_name, self.parameters, \
                self.parameters_ext, self.name)

    @staticmethod
    def bg_running(self):
        '''get data from sina and save in db'''
        pass

    @staticmethod
    def on_change_price(target, value, oldvalue, initiator):
        print 'change %s: %s' % (target.code, value)
        pass

db.event.listen(BacktestingLog.parameters, 'set', BacktestingLog.on_change_price)





