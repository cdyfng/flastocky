from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import bollinger
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import trades
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import drawdown
import logging
import os

logging.basicConfig(level=logging.ERROR,\
    format='%(asctime)s|%(filename)s|%(funcName)s|line:%(lineno)d|%(levelname)s|%(message)s',
    datefmt='%Y-%m-%d %X',
    filename=os.path.dirname(os.path.abspath(__file__)) +'/bbandsAll.log'
    )



class BBandsAll(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        super(BBandsAll, self).__init__(feed)
        self.__instrument = instrument
        self.setUseAdjustedValues(True)
        #feed[instrument].setUseAdjustedValues(True)
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(), bBandsPeriod, 2)
        #self.__bbands = bollinger.BollingerBands(feed[instrument].getAdjCloseDataSeries() , bBandsPeriod, 2)

    def getBollingerBands(self):
        return self.__bbands

    def onBars(self, bars):
        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower is None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]
        #if shares == 0 and bar.getClose() < lower:
        if shares == 0 and bar.getAdjClose() < lower:

            sharesToBuy = int(self.getBroker().getCash(False) / bar.getAdjClose())
            #print 'buy', bar.getAdjClose(), lower, sharesToBuy
            self.marketOrder(self.__instrument, sharesToBuy)
        elif shares > 0 and bar.getAdjClose() > upper:
            #print 'sell', bar.getAdjClose(), upper
            self.marketOrder(self.__instrument, -1*shares)


def main(plot, code):
    #instrument = "yhoo"
    #.SS .SZ

    instrument = code + (".SS" if(code[0:3]== '600') else ".SZ")
    bBandsPeriod = 13

    # Download the bars.
    feed = yahoofinance.build_feed([instrument], 2015, 2016, "./data")

    strat = BBandsAll(feed, instrument, bBandsPeriod)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    retAnalyzer = returns.Returns()
    strat.attachAnalyzer(retAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    strat.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    strat.attachAnalyzer(tradesAnalyzer)

    tradesAnalyzer = trades.Trades()
    strat.attachAnalyzer(tradesAnalyzer)
    ##print 'retAnalyzer.getReturns()[-1]:', retAnalyzer.getReturns()[-1]
    ##print 'size retAnalyzer.getReturns()[-1]:', len(retAnalyzer.getReturns()[-1])

    #print 'last price:',strat.getLastPrice(instrument)
    #print  len(feed)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("upper", strat.getBollingerBands().getUpperBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("middle", strat.getBollingerBands().getMiddleBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("lower", strat.getBollingerBands().getLowerBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("price", feed[instrument].getAdjCloseDataSeries())

    strat.run()
    #print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    #logger.info("%s value: $%.2f" % (code, strat.getResult()))
    #logger.getLogger("custom").info("ble")
    logging.info("%s value: $%.2f" % (code, strat.getResult()))
    print "Final portfolio value: $%.2f" % strat.getResult()
    print "Cumulative returns: %.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100)
    print "Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0.05))
    print "Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100)
    print "Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration())

    print
    print "Total trades: %d" % (tradesAnalyzer.getCount())
    if tradesAnalyzer.getCount() > 0:
        profits = tradesAnalyzer.getAll()
        print "Avg. profit: $%2.f" % (profits.mean())
        print "Profits std. dev.: $%2.f" % (profits.std())
        print "Max. profit: $%2.f" % (profits.max())
        print "Min. profit: $%2.f" % (profits.min())
        returns0 = tradesAnalyzer.getAllReturns()
        print "Avg. return: %2.f %%" % (returns0.mean() * 100)
        print "Returns std. dev.: %2.f %%" % (returns0.std() * 100)
        print "Max. return: %2.f %%" % (returns0.max() * 100)
        print "Min. return: %2.f %%" % (returns0.min() * 100)

    print
    print "Profitable trades: %d" % (tradesAnalyzer.getProfitableCount())
    if tradesAnalyzer.getProfitableCount() > 0:
        profits = tradesAnalyzer.getProfits()
        print "Avg. profit: $%2.f" % (profits.mean())
        print "Profits std. dev.: $%2.f" % (profits.std())
        print "Max. profit: $%2.f" % (profits.max())
        print "Min. profit: $%2.f" % (profits.min())
        returns0 = tradesAnalyzer.getPositiveReturns()
        print "Avg. return: %2.f %%" % (returns0.mean() * 100)
        print "Returns std. dev.: %2.f %%" % (returns0.std() * 100)
        print "Max. return: %2.f %%" % (returns0.max() * 100)
        print "Min. return: %2.f %%" % (returns0.min() * 100)

    print
    print "Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount())
    if tradesAnalyzer.getUnprofitableCount() > 0:
        losses = tradesAnalyzer.getLosses()
        print "Avg. loss: $%2.f" % (losses.mean())
        print "Losses std. dev.: $%2.f" % (losses.std())
        print "Max. loss: $%2.f" % (losses.min())
        print "Min. loss: $%2.f" % (losses.max())
        returns0 = tradesAnalyzer.getNegativeReturns()
        print "Avg. return: %2.f %%" % (returns0.mean() * 100)
        print "Returns std. dev.: %2.f %%" % (returns0.std() * 100)
        print "Max. return: %2.f %%" % (returns0.max() * 100)
        print "Min. return: %2.f %%" % (returns0.min() * 100)


    if plot:
        plt.plot()

def get_list_hs300():
    import tushare as ts
    return ts.get_hs300s()

if __name__ == "__main__":
    #main(False)
    ##hs300 = get_list_hs300()
    ##print type(hs300), len(hs300)
    #print hs300.describe()
    #print hs300[1:len(hs300)]
    ##for code in hs300.code:
    ##    print code
        #main(True, '300033')
    try:
        #main(False, code)
        main(True, '002594')
        #main(True, '600999')
    except:
        pass


    pass
