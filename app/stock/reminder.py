import re, os, thread
import warningEmail
from flask import current_app

class Notify():
    def __init__(self, stock_id, price_interval_percent, \
                 base_price, bench_price):
        self.stock_id = stock_id
        self.price_interval_percent = price_interval_percent
        self.price_threshold_low = 0.0
        self.price_threshold_high = 0.0
        self.base_price = base_price
        self.bench_price = bench_price
        self.is_stop = False
        #return self

    def run(self, now_price):
        print self.stock_id, now_price
        price = now_price
        if price != -1 and price !=0 :
            if self.price_threshold_low == 0:
                threshold_unit = self.base_price * self.price_interval_percent
                self.price_threshold_low = self.base_price - threshold_unit
                self.price_threshold_high = self.base_price + threshold_unit
                print 'init %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
            if price >= self.price_threshold_high:
                threshold_unit = self.base_price * self.price_interval_percent
                self.price_threshold_high += threshold_unit
                self.price_threshold_low += threshold_unit
                self.base_price += threshold_unit
                print 'high notify %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                subject = self.stock_id + ' high ' +  str(self.price_interval_percent)

                content = 'now: %.2f bench: %.2f rate: %.2f' \
                    %(price, self.bench_price, \
                    (price - self.bench_price)/self.bench_price * 100.0)
                print subject + '\n' + content
                self.emailNotify(subject, content)

            if price <= self.price_threshold_low:
                threshold_unit = self.base_price * self.price_interval_percent
                self.price_threshold_high -= threshold_unit
                self.price_threshold_low -= threshold_unit
                self.base_price -= threshold_unit
                print 'low notify %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                subject = self.stock_id + ' low ' + str(self.price_interval_percent)
                content = 'now: %.2f bench: %.2f rate: %.2f' \
                    %(price, self.bench_price, \
                    (price - self.bench_price)/self.bench_price *100.0 )
                print subject + '\n' + content
                self.emailNotify(subject, content)

    def emailNotify(self, subject, content):
        wemail = warningEmail.warningEmail()
        #wemail.send(subject, content)
        try:
            thread.start_new_thread(wemail.send, (subject, content, ))
        except:
               print "Error: unable to start thread"
        self.saveConfig()
        print self.stock_id, 'send email'

    def saveConfig(self):
        stocks =  readStocks()
        for n in stocks:
            if n.stock_id == self.stock_id :
                n.base_price = self.base_price
                print '%s %f %f changed'%\
                    (n.stock_id, n.base_price, n.bench_price)
        saveStocks(stocks)


    def __repr__(self):
        return '%s %f' % (self.stock_id, self.bench_price)


class Reminder():
    Rmds = []
    RiseTop = {}
    RiseTopOpen = {}
    FallBottom = {}
    FallBottomOpen = {}
    id_name_dict = None

    def __init__(self):
        #Reminder.Rmds = []
        if(len(Reminder.Rmds) == 0):
            Reminder.Rmds = readStocks()
            #check if 0 again
            if(len(Reminder.Rmds) == 0):
                print 'config file import error'
                Reminder.Rmds.append(Notify('null',0,0,0))

        if Reminder.id_name_dict == None:
            from ..models_stock import Baseinfo
            Reminder.id_name_dict = Baseinfo.get_id_name_dict()
            current_app._logger.info('get stock_id stock_name dict ok')

    def add(self, item):
        self.remove(item)
        Reminder.Rmds.append(item)

    def remove(self, item):
        if item in Reminder.Rmds:
            Reminder.Rmds.remove(item)

    @staticmethod
    def run(target, now_price):
        if(len(Reminder.Rmds) == 0):
            r = Reminder()
        #if target.yesterday_closing_price
        riseLimit = target.yesterday_closing_price * 1.1
        fallLimit = target.yesterday_closing_price * 0.9
        s = '%s %f %f %f %f %f %f'% (target.stock_id, \
            target.yesterday_closing_price, \
            now_price, target.high_price, target.low_price, \
            riseLimit, fallLimit)
        print s
        if target.high_price >= riseLimit:
            if Reminder.RiseTop.get(target.stock_id) is None:
                #current_app._logger.info(s)
                s = '%s %s %f riseTop first add' % \
                    (target.stock_id, \
                     Reminder.id_name_dict[target.stock_id], \
                     now_price)
                current_app._logger.info(s)
            Reminder.RiseTop[target.stock_id] = [now_price,]
            if now_price < target.high_price:
                if Reminder.RiseTopOpen.get(target.stock_id) is None:
                    s = '%s %s %f riseTopOpen first add' % \
                    (target.stock_id, \
                     Reminder.id_name_dict[target.stock_id], \
                     now_price)
                    current_app._logger.info(s)
                Reminder.RiseTopOpen[target.stock_id]=[now_price,]

        if target.low_price <= fallLimit:
            if Reminder.FallBottom.get(target.stock_id) is None:
                #current_app._logger.info(s)
                s = '%s %s %f FallBottom first add' % \
                    (target.stock_id, \
                     Reminder.id_name_dict[target.stock_id], \
                     now_price)
                current_app._logger.info(s)
            Reminder.FallBottom[target.stock_id] = [now_price,]
            if now_price > target.low_price:
                if Reminder.FallBottomOpen.get(target.stock_id) is None:
                    s = '%s %s %f FallBottomOpen first add' % \
                        (target.stock_id, \
                         Reminder.id_name_dict[target.stock_id], \
                         now_price)
                    current_app._logger.info(s)
                Reminder.FallBottomOpen[target.stock_id]=[now_price,]



        #remind price change when it satisfy the notify remind
        for notify in Reminder.Rmds:
            if notify.stock_id == target.stock_id:
                notify.run(now_price)

        #remind the stock when

    def __repr__(self):
        s = ''
        for item in Reminder.Rmds:
            s = ''.join([s, '%s %f \n' % (item.stock_id, item.bench_price)])
        return s

cur_dir = os.path.dirname(os.path.abspath(__file__))
def readStocks():
    listStocks = []
    stockRe = re.compile('(.*),(.*),(.*),(.*),(.*),(.*)')
    for line in open(cur_dir + '/config.ini').readlines():
        if line.startswith('#'):
            continue
        line = line.strip()
        m = stockRe.search(line)
        if m:
                stockId, percent, startPrice, \
                    lowNotifyPrice, highNotifyPrice, benchPrice \
                    = m.groups()
                #print stockId, startPrice, percent, \
                #    lowNotifyPirce, highNotifyPrice, nowPrice
                listStocks.append(Notify(str(stockId),float(percent),\
			float(startPrice), float(benchPrice)))
    return listStocks

def saveStocks(listStocks):
    stockconfig = open(cur_dir + '/config.ini','wt')
    for n in listStocks:
        w=str(n.stock_id)+','+str(n.price_interval_percent) + ','+\
            str(n.base_price) + ',0.0,0.0,' + str(n.bench_price)
        stockconfig.write(w)
        stockconfig.write('\n')
    stockconfig.close

