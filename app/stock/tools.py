#!/upplication context is created and destroyed as necessary. It never moves between threads and it will not be shared between requests. As such it is the perfect place to store database connection information and other things. The internal stack object is calledsr/bin/env python
# -*- coding: utf-8 -*-
PAGESIZE = 700
WEB_TIME_OUT = 5
DM_TIME_OUT = 10
#API
TOT_PARAMS = 33


from datetime import datetime,timedelta
import os, time, re
import httplib2
from bs4 import BeautifulSoup

def data_parser(data):
    """
    return a dict:
    key is a tuple (stock_id, date, time)
    value is a tuple contains parameters in the following order
    (
        open_price, yesterday_closing_price,
        now_price, high_price, low_price,
        now_buy_price, now_sell_price, #same as buy_1_price and sell_1_price
        volume, amount,
        buy_1_vol, buy_1_price,
        buy_2_vol, buy_2_price,
        buy_3_vol, buy_3_price,
        buy_4_vol, buy_4_price,
        buy_5_vol, buy_5_price,
        sell_1_vol, sell_1_price,
        sell_2_vol, sell_2_price,
        sell_3_vol, sell_3_price,
        sell_4_vol, sell_4_price,
        sell_5_vol, sell_5_price
    )
    """
    global TOT_PARAMS
    ret = dict()
    lines = data.split('\n')
    for line in lines:

        eq_pos = line.find('=')
        if eq_pos == -1:
            continue

        params_seg = line[eq_pos + 2:-1]
        params = params_seg.split(',')
        if len(params) != TOT_PARAMS:
            continue

        stock_id_seg = line[:eq_pos]
        stock_id = stock_id_seg[stock_id_seg.rfind('_') + 1:]
        date = params[30]
        time = params[31]
        #params[32] is nothing

        key = (stock_id, date, time)

        value = tuple(params[1:30])

        ret[key] = value
    return ret


def get_name_price(data):
    """
    return name and price of stocks:
    data in is the following order
    (
        open_price, yesterday_closing_price,
        now_price, high_price, low_price,
        now_buy_price, now_sell_price, #same as buy_1_price and sell_1_price
        volume, amount,
        buy_1_vol, buy_1_price,
        buy_2_vol, buy_2_price,
        buy_3_vol, buy_3_price,
        buy_4_vol, buy_4_price,
        buy_5_vol, buy_5_price,
        sell_1_vol, sell_1_price,
        sell_2_vol, sell_2_price,
        sell_3_vol, sell_3_price,
        sell_4_vol, sell_4_price,
        sell_5_vol, sell_5_price
    )
    """
    global TOT_PARAMS
    ret = dict()
    lines = data.split('\n')
    for line in lines:

        eq_pos = line.find('=')
        if eq_pos == -1:
            continue

        params_seg = line[eq_pos + 2:-1]
        params = params_seg.split(',')
        if len(params) != TOT_PARAMS:
            continue

        stock_id_seg = line[:eq_pos]
        stock_id = stock_id_seg[stock_id_seg.rfind('_') + 1:]

        #date = params[30]
        #time = params[31]
        #params[32] is nothing

        #key = (stock_id, date, time)
        key = stock_id

        #value = tuple(params[1:30])
        value = tuple([params[0].decode('gbk'), \
                       float(params[3])])

        ret[key] = value
    return ret


def ensure_dir(file_name):
    root_dir = os.path.dirname(file_name)
    if root_dir == '':
        root_dir == '.'
    if not os.path.exists(root_dir):
        ensure_dir(root_dir)
        os.makedirs(root_dir)


def get_beijing_time():
    return datetime.utcnow() + timedelta(hours =+ 8)


def httpGetContent(url, headers=None, charset=None):
    "httplib2处理请求"
    try:
        http = httplib2.Http()
        request, content = http.request(uri=url, headers=headers)
        if request.status == 200 and content:
            if charset:
                return content.decode(charset).encode('utf8')
            else:
                return content
    except Exception as e:
        raise e


def is_trade_time():
    today = int(time.strftime("%w"))
    if today ==0 or today == 6: return False
    #return True
    current_beijing_hms = get_beijing_time().strftime('%H:%M:%S')
    if current_beijing_hms < '09:25:00':
        return False
    if current_beijing_hms > '11:35:00' and current_beijing_hms < '12:55:00':
        return False
    if current_beijing_hms > '15:05:00':
        return False
    return True


def read_code(file_name, prefix):
    code_file = open(file_name)
    ret = []
    for code in code_file:
        code = code.strip()
        ret.append(prefix + code)
    return ret


def validate_decimal(value):
    """
    验证小数数据
    """
    if value:
        try:
            regex = re.compile(r'^([0-9]{1,}[.][0-9]*|-[0-9]{1,}[.][0-9]*|\d+|-\d+)')
            value = re.findall(regex, value)[0]
            return decimal(value)
        except Exception as e:
            return 0


def decimal(value):
    try:
        if value and value != "":
            return float(value)
    except Exception as e:
        return 0.0


def stock_base_info(code):
    """
    得到股票其他的基础数据信息
    包含：
    pe_trands 市盈率（动态）：47.98
    type 分类 ：big（大盘股）medium （中盘股）small（小盘股）
    pe_static 市盈率（静态）：8.61
    total_capital 总股本 44.7亿股
    ciculate_capital 流通股本 44.7亿股
    pb 市净率 1.24

    """
    url = "http://basic.10jqka.com.cn/%s/" % code
    content = httpGetContent(url)
    if content:
        stock_dict = {}
        soup = BeautifulSoup(content)
        profile = soup.select('div#profile')

        table = profile[0].select('table')[0]
        td_list = table.select('td')
        td_select_key = lambda td: td.select('span')[0].text.strip().replace('\t','')
        td_select_value = lambda td: td.select('span')[1].text.strip().replace('\t','')
        for i, td in enumerate(td_list):
            #print td_select_key(td), td_select_value(td)
            #stock_dict[td_select_key(td)] = td_select_value(td)
            if i == 0:    # 主营业务：
                stock_dict["main_busyness"] = td_select_value(td)
            elif i == 1:    # 所属行业：
                stock_dict["industry"] = td_select_value(td)
            elif i == 2:    # 涉及概念：
                stock_dict["concept"] = td_select_value(td)

        table = profile[0].select('table')[1]
        td_list = table.select('td')
        td_select_key = lambda td: td.select('span')[0].text.strip().replace('\t','')
        #td_select_value = lambda td: td.select('span')[1].text.strip().replace('\t','')
        td_select = lambda td: td.select('span')[1].text.strip().replace('\t','')
        for i, td in enumerate(td_list):
            #print td_select_key(td), td_select_value(td)
            #stock_dict[td_select_key(td)] = td_select_value(td)
            stock_dict["code"] = code
            if i == 0:    # 市盈率(动态)：
                stock_dict["pe_ratio_dynamic"] = validate_decimal(td_select(td))
            elif i == 2:  # 净资产收益率
                stock_dict['return_on_equity'] = validate_decimal(td_select(td))
            elif i == 3:  # 分类
                text = td_select(td)
                if text == u"大盘股":
                    stock_dict['type'] = 'big'
                elif text == u'中盘股':
                    stock_dict['type'] = 'medium'
                elif text == u"小盘股":
                    stock_dict['type'] = 'small'
                else:
                    stock_dict['type'] = text
            elif i == 4:  # 市盈率(静态)
                stock_dict['pe_ratio_static'] = validate_decimal(td_select(td))
            elif i == 5:  # 营业收入
                stock_dict['income'] = validate_decimal(td_select(td))
            elif i == 6:  # 每股净资产
                stock_dict['assert_per_share'] = validate_decimal(td_select(td))
            elif i == 7:  # 总股本
                stock_dict['total_capital'] = validate_decimal(td_select(td))
            elif i == 8:  # 市净率
                stock_dict['pb'] = validate_decimal(td_select(td))
            elif i == 9:  # 净利润
                stock_dict['net_profit'] = validate_decimal(td_select(td))
            elif i == 10:  # 每股现金流
                stock_dict['cash_flow_per_share'] = validate_decimal(td_select(td))
            elif i == 11: # 流通股本
                stock_dict['circulate_capital'] = validate_decimal(td_select(td))


        #for item in stock_dict:
        #    print item, stock_dict[item]

        return stock_dict


if __name__=='__main__':
    pass



