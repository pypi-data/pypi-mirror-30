# encoding: utf-8
"""
@author: cb_Lian
@version: 1.0
@license: Apache Licence
@file: TradeInterface.py
@time: 2018/3/13 16:11
@Function：This interface is designed for people who use haizhi licai to realise
           simulate-trading stocks
"""
import json
import urllib2
import urllib
import hashlib
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


class Trade:
    """
    参数说明: 1.userId，用户Id，需在海知平台注册获得，默认'',必须设置
              2.password，用户密码，海知平台注册时用户所设，默认'',必须设置
              3.buy_sell 取值为'buy'、'sell',必须设置
              4.code，买卖股票代码,必须设置
              5.volume，买卖数量，必须设置
              6.price，买卖的价格,在price_type 为limit_price时必须设置
              7.price_type，买卖价格的类型，取值为‘limit_price’、‘now_price’，必须设置
              8.effect_term，委托的期限，取值为1,2,3……，1代表今天，2代表明天，其他依此类推

    """

    def __init__(self, userid='', password=''):
        self.prefix = "http://www.haizhilicai.com/"
        # self.prefix = "http://192.168.0.136/"
        self.trade_url = self.prefix + 'Tradeinterface/get_tradeinfo'
        self.prof_info_url = self.prefix + 'Tradeinterface/get_profit_info'
        self.stock_encode_name = 'tradeinfo'
        self.query_pro_encode_name = 'profit_info'

        self.send_dic = {'userid': '', 'password': '', 'stock_dic_ls': list()}
        self.set_userid(userid)
        self.set_password(password)
        # self.url = 'http://www.haizhilicai.com/Tradeinterface/get_tradeinfo'

    # 设置用户id
    def set_userid(self, userid=''):
        userid = str(userid)
        if userid.strip() != '':
            self.send_dic['userid'] = userid
            return True
        else:
            return False

    # 设置用户密码
    def set_password(self, password=''):
        password = str(password)
        if password.strip() != '':
            self.send_dic['password'] = self.md5encryption(password)
            return True
        else:
            return False

    # 设置买卖股票列表
    def set_stock_dic_ls(self, stock_dic_ls=list()):
        if len(stock_dic_ls) > 0:
            self.send_dic['stock_dic_ls'] = stock_dic_ls
            return True
        else:
            return False

    # 设置买卖股票列表模板
    @staticmethod
    def get_stock_dic():
        stock_dic = {'price': '', 'price_type': '', 'effect_term': '', 'buy_sell': '', 'volume': '', 'code': ''}
        return stock_dic

    # 实现md5加密
    @staticmethod
    def md5encryption(password):
        if password.strip() != '':
            md = hashlib.md5()
            md.update(password)
            return md.hexdigest()
        else:
            return ''

    # 判断字符串是否是正浮点数
    @staticmethod
    def is_positive_float(astring):
        astring = str(astring)
        try:
            x = float(astring)
            if x > 0:
                return True
            else:
                return False
        except:
            return False

    # 判断字符串是否是正整数
    @staticmethod
    def is_positive_int(astring):
        astring = str(astring)
        try:
            if (astring.isdigit()) and (int(astring) > 0):
                return True
            else:
                return False
        except:
            return False

    # 判断字符串是否是100的倍数
    @staticmethod
    def is_multiple_hund(astring):
        astring = str(astring)
        if (int(astring) % 100) != 0:
            return False
        else:
            return True

    # 判断是否是限价和市价
    @staticmethod
    def exist_price_type(astring):
        astring = str(astring)
        if astring in ['limit_price', 'now_price']:
            return True
        else:
            return False

    # 解析json
    @staticmethod
    def parse_res(temp_res):
        try:
            resls = json.loads(temp_res)
            res_str = ""
            for x in resls:
                res_str = res_str + x + '\n'
        except:
            res_str = temp_res
        return res_str

    # # 设置资金比例，暂不使用
    # def set_cash_ratio(self, cash_ratio):
    #     cash_ratio = str(cash_ratio)
    #     if self.isnumber(cash_ratio) is True:
    #         self.send_dic['cash_ratio'] = cash_ratio
    #         return True
    #     else:
    #         return False

    # # 验证现金比例是否是大于0小于1的浮点数，暂不使用
    # def validate_cash_ratio(self, cash_ratio):
    #     if self.isnumber(cash_ratio) is True:
    #         if float(cash_ratio) < 0.0 or float(cash_ratio) > 1.0:
    #             return "cash_ratio should be between 0 and 1 !"
    #         else:
    #             return True
    #     else:
    #         return "cash_ratio should be float!"

    # 定义买交易
    def buy(self):
        buy_sell_type = 'buy'
        return self.trade_stock(self.send_dic, buy_sell_type, self.stock_encode_name, self.trade_url)

    # 定义卖交易
    def sell(self):
        buy_sell_type = 'sell'
        return self.trade_stock(self.send_dic, buy_sell_type, self.stock_encode_name, self.trade_url)

    # 定义基本验证:用户id、用户password
    def basic_vali(self):
        # 用户id为空
        if self.send_dic['userid'] == '':
            return "userid attribute can't be a blank string!"
        # 用户密码为空
        if self.send_dic['password'] == '':
            return "password attribute can't be a blank string!"
        else:
            return True

    # 定义股票列表验证
    def stockls_vali(self, buy_sell_type):
        attr_ls = set(['price', 'price_type', 'effect_term', 'buy_sell', 'volume', 'code'])
        temp_stock_dic_ls = self.send_dic['stock_dic_ls']
        if len(temp_stock_dic_ls) == 0:  # 股票列表为空
            return "stock info must be needed!"
        else:  # 验证dic的键和值
            for stock_dic in temp_stock_dic_ls:
                subset = set(stock_dic.keys()) - set(attr_ls)
                if (len(stock_dic) == 6) and (len(subset) == 0):
                    if not stock_dic['buy_sell'] == buy_sell_type:   # 买卖标志为buy或sell
                        return buy_sell_type+" function buy_sell should be " + buy_sell_type + "!"

                    if self.is_positive_int(stock_dic['code']) is not True:  # 股票代码为正整数
                        return "code should be positive int!"

                    if self.is_positive_int(stock_dic['volume']) is not True:  # 交易量为正整数
                        return "volume should be positive int!"
                    elif self.is_multiple_hund(stock_dic['volume']) is not True:  # 交易量为100的倍数
                        return "volume should be multiple of 100!"

                    if self.exist_price_type(stock_dic['price_type']) is not True:  # price_type为limit_price或now_price
                        return "price_type should be limit_price or now_price!"

                    elif stock_dic['price_type'] == 'limit_price':  # 如果为限价，必须设置价格
                        if self.is_positive_float(stock_dic['price']) is not True:  # price为正浮点数
                            return "limit_type price should be positive float!"

                    if self.is_positive_int(stock_dic['effect_term']) is not True:  # effect_term为正整数
                        return "effect_term should be positive int!"
                else:
                    return "stock_dic must be six normal attributions!"
        return True

    # 发起交易请求
    @staticmethod
    def http_post(send_dic, urlencode_name, url):
        jdata = json.dumps(send_dic)  # json格式化编码
        jdata = urllib.urlencode({urlencode_name: jdata})  # urlencode编码
        req = urllib2.Request(url, jdata)  # 生成页面请求的完整数据
        res = urllib2.urlopen(req)  # 发送页面请求
        temp_res = res.read()  # 返回结果，把list结果处理为字符串显示
        return temp_res

    # 买卖请求验证与交易
    def trade_stock(self, send_dic, buy_sell_type, stock_encode_name, trade_url):
        basic_vali_res = self.basic_vali()
        stockls_vali_res = self.stockls_vali(buy_sell_type)
        if basic_vali_res is not True:  # 基本信息验证
            return basic_vali_res
        if stockls_vali_res is not True:  # 股票信息验证
            return stockls_vali_res
        temp_res = self.http_post(send_dic, stock_encode_name, trade_url)  # 发起请求
        return self.parse_res(temp_res)

    # 解析收益率
    @staticmethod
    def parse_profit(res):
        try:
            resls = json.loads(res)
            res_ls = []
            if len(resls['data_user']) > 0:
                res_ls.append((u'all', resls['data_user']['profit_rate']))
            else:
                res_ls.append((u'无用户信息',))
            if len(resls['data_stock']) > 0:
                for stock in resls['data_stock']:
                    res_ls.append((stock['SecurityID'], stock['cur_profit']))
            else:
                res_ls.append((u'无持仓信息',))
        except:
            res_ls = (res,)
        res_ls = tuple(res_ls)
        return res_ls

    # 请求收益率
    def query_profit(self):
        basic_vali_res = self.basic_vali()
        if basic_vali_res is not True:  # 基本信息验证
            return basic_vali_res
        temp_res = self.http_post(self.send_dic, self.query_pro_encode_name, self.prof_info_url)  # 发起请求
        return self.parse_profit(temp_res)


if __name__ == '__main__':
    trade = Trade()
    print "".isdigit()
