#!/usr/bin/env python
#coding=utf-8
import itertools,json
from pyalgotrade.optimizer import local
from pyalgotrade.tools import yahoofinance
import bbandsAll
import logging,os
from app.models_quanter import BacktestingLog
from app  import db
#from .. import db

logger1 = logging.getLogger('mylogger')
logger1.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.dirname(os.path.abspath(__file__)) +'/bbandsAll2.log')

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()

# 定义handler的输出格式formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger1.addHandler(fh)
logger1.addHandler(ch)

def parameters_generator():
    instrument = ['300104.SZ']
    entrySMA = range(250, 251)
    exitSMA = range(15, 16)
    rsiPeriod = range(2, 11)
    overBoughtThreshold = range(90, 98)
    overSoldThreshold = range(25, 30)
    return itertools.product(instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)


def parameters_generator_sma():
    instrument = ['002594.SZ']
    entrySMA = range(5, 50)
    #exitSMA = range(5, 16)
    #rsiPeriod = range(2, 11)
    #overBoughtThreshold = range(75, 96)
    #overSoldThreshold = range(5, 26)
    #return itertools.product(instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)
    return itertools.product(instrument, entrySMA)

def parameters_generator_bBandsPeriod():
    #instrument = ['002594.SZ']
    instrument = ['600999.SS']
    bBandsPeriod = range(5, 50)
    return itertools.product(instrument, bBandsPeriod)


def parameters_generator_bBandsPeriod_list(code):
    #instrument = ['002594.SZ']
    #instrument = ['600999.SS']
    instrument=[code]
    #instrument.append(code)
    bBandsPeriod = range(5, 50)
    return itertools.product(instrument, bBandsPeriod)

def get_list_hs300():
    import tushare as ts
    return ts.get_hs300s()

def run_bband(code, from_year, end_year):
    #instrument = '300104.SZ'
    instrument = code + (".SS" if (code[0:3] == '600') else ".SZ")
    feed = yahoofinance.build_feed([instrument], from_year, end_year, "./data")
    #run = local.run(rsi2.RSI2, feed, parameters_generator())
    print 'run in '
    run = local.run(bbandsAll.BBandsAll, feed, parameters_generator_bBandsPeriod_list(instrument))
    print 'run result:', run.getParameters(), run.getResult()
    return run

# The if __name__ == '__main__' part is necessary if running on Windows.
    # Load the feed from the CSV files.
    #instrument = '002594.SZ'
    #instrument = '600999.SS'
    #code = '600999.SS'


def main():
    hs300 = get_list_hs300()
    i = 0
    from_year = 2014
    end_year =2014
    paras = 'null'
    for code in hs300.code[0:2]:
        print code
        d = {}
        try:
            run = run_bband(code, from_year, end_year)
            logger1.info('run result: %s    %d    %f    %s'
                         % (run.getParameters()[0], run.getParameters()[1], run.getResult(), hs300.name[i]))

            d['code'] = run.getParameters()[0]
            d['param'] = run.getParameters()[1]
            d['value'] = run.getResult()
            d['period'] = str(from_year) + '-' + str(end_year)

        except:
            logger1.info('%s error  ', code)
            pass

        # name= hs300.name[i].decode("unicode_escape")
        btl = BacktestingLog(code=code,strategy_name='bband',parameters=json.dumps(d))
        print hs300.name[i]
        db.session.add(btl)
        db.session.commit()

        i = i + 1

    logger1.info('bband calculate over  ')
    ##code = '300104.SZ'
    ##feed = yahoofinance.build_feed([code], 2014, 2015, "./data")
    #run = local.run(rsi2.RSI2, feed, parameters_generator())
    ##print 'run in '
    ##run = local.run(bbandsAll.BBandsAll, feed, parameters_generator_bBandsPeriod_list(code))
    ##print 'run result: ', run.getParameters(), run.getResult()
    #print run


if __name__ == '__main__':
    main()
