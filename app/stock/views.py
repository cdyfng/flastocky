from flask import render_template
from ..models_stock import Stock, Baseinfo
from .. import db
from . import stock


@stock.route('/')
def stockid():
    s = Stock(stock_id='sh600036',
              timestamp='2014-01-24 00:33:33',
              open_price = 12,
              yesterday_closing_price = 12,
              now_price = 11,
              high_price = 11,
              low_price = 11)
    db.session.add(s)
    db.session.commit()
    #print db
    return '<h1>add ok </h1>'


@stock.route('/list')
def list():
    baseinfos = Baseinfo.query.all()
    #pagination = Baseinfo.query\
    #    .order_by(Baseinfo.timestamp.desc())\
    #    .paginate(1, per_page=20)
    #baseinfos = pagination.items
    return render_template('stock/list.html',
                           baseinfos = baseinfos)



