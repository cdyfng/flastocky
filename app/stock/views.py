from flask import render_template, redirect, url_for
#from ..models_stock import Stock, Baseinfo
from ..models_stock import Baseinfo
from .forms import StockIdForm
#from .. import db
from . import stock


@stock.route('/', methods=['GET', 'POST'])
def main():
    form = StockIdForm()
    if form.validate_on_submit():
        stockid = form.stock_id.data
        print stockid
        return redirect(url_for('.baseinfo', stockid = stockid))

    return render_template('/stock/index.html', form=form)


@stock.route('/list')
def list():
    form = StockIdForm()
    baseinfos = Baseinfo.query.all()
    if form.validate_on_submit():
         stockid = form.stock_id.data
         print stockid
         return redirect(url_for('.baseinfo', stockid = stockid))
    #pagination = Baseinfo.query\
    #    .order_by(Baseinfo.timestamp.desc())\
    #    .paginate(1, per_page=20)
    #baseinfos = pagination.items
    return render_template('stock/list.html',\
                           form=form, \
                           baseinfos = baseinfos)


@stock.route('/<stockid>', methods=['Get', 'Post'])
def baseinfo(stockid):
    form = StockIdForm()
    if form.validate_on_submit():
         stockid = form.stock_id.data
         print stockid
         return redirect(url_for('.baseinfo', stockid = stockid))

    baseinfos = []
    try:
        baseinfos = Baseinfo.query.filter_by(stock_id=stockid)\
            .all()
    except Exception as e:
        print e
    #return '<h1> ok </h1>'
    return render_template('/stock/list.html', \
                           form=form, \
                           baseinfos=baseinfos)


