# encoding: UTF-8

import sys
import json
from time import sleep

from PyQt4 import QtGui

from vnctpmd import *


# ----------------------------------------------------------------------
def print_dict(d):
    """按照键值打印一个字典"""
    for key, value in d.items():
        print key + ':' + str(value)


# ----------------------------------------------------------------------
def simple_log(func):
    """简单装饰器用于输出函数名"""

    def wrapper(*args, **kw):
        print ""
        print str(func.__name__)
        return func(*args, **kw)

    return wrapper


########################################################################

def enum(**enums):
    return type('Enum', (), enums)


# 仓位变化方向
open_interest_delta_forward_enum = enum(OPEN="Open", CLOSE="Close", EXCHANGE="Exchange", NONE="None",
                                        OPENFWDOUBLE="OpenFwDouble", CLOSEFWDOUBLE="CloseFwDOuble")
# 订单成交区域，决定是多还是空
order_forward_enum = enum(UP="Up", DOWN="Down", MIDDLE="Middle")

# 最终需要的tick方向
tick_type_enum = enum(OPENLONG="OpenLong", OPENSHORT="OpenShort", OPENDOUBLE="OpenDouble",
                      CLOSELONG="CloseLong", CLOSESHORT="CloseShort", CLOSEDOUBLE="CloseDouble",
                      EXCHANGELONG="ExchangeLong", EXCHANGESHORT="ExchangeShort",
                      OPENUNKOWN="OpenUnkown", CLOSEUNKOWN="CloseUnkown", EXCHANGEUNKOWN="ExchangeUnkown",
                      UNKOWN="Unkown", NOCHANGE="NoChange")

tick_color_enum = enum(RED="Red", GREEN="Green", WHITE="White")

tick_type_key_enum = enum(TICKTYPE="TickType", TICKCOLOR="TickColor")

# 只与计算对手单的组成相关
opponent_key_enum = enum(OPPOSITE="Opposite", SIMILAR="Similar")

# 只做翻译成中文使用，对应 tick_type_enum
tick_type_str_dict = {tick_type_enum.OPENLONG: "多开", tick_type_enum.OPENSHORT: "空开",
                      tick_type_enum.OPENDOUBLE: "双开",
                      tick_type_enum.CLOSELONG: "多平", tick_type_enum.CLOSESHORT: "空平",
                      tick_type_enum.CLOSEDOUBLE: "双平",
                      tick_type_enum.EXCHANGELONG: "多换", tick_type_enum.EXCHANGESHORT: "空换",
                      tick_type_enum.OPENUNKOWN: "未知开仓", tick_type_enum.CLOSEUNKOWN: "未知平仓",
                      tick_type_enum.EXCHANGEUNKOWN: "未知换仓",
                      tick_type_enum.UNKOWN: "未知", tick_type_enum.NOCHANGE: "没有变化",
                      tick_color_enum.RED: "红", tick_color_enum.GREEN: "绿", tick_color_enum.WHITE: "白"}

# 根据 open_interest_delta_forward_enum 和 order_forward_enum 计算出tick类型的字典
tick_type_cal_dict = {
    open_interest_delta_forward_enum.NONE:
        {
            order_forward_enum.UP: {tick_type_key_enum.TICKTYPE: tick_type_enum.NOCHANGE,
                                    tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE},
            order_forward_enum.DOWN: {tick_type_key_enum.TICKTYPE: tick_type_enum.NOCHANGE,
                                      tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE},
            order_forward_enum.MIDDLE: {tick_type_key_enum.TICKTYPE: tick_type_enum.NOCHANGE,
                                        tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE}
        },
    open_interest_delta_forward_enum.EXCHANGE:
        {
            order_forward_enum.UP: {tick_type_key_enum.TICKTYPE: tick_type_enum.EXCHANGELONG,
                                    tick_type_key_enum.TICKCOLOR: tick_color_enum.RED},
            order_forward_enum.DOWN: {tick_type_key_enum.TICKTYPE: tick_type_enum.EXCHANGESHORT,
                                      tick_type_key_enum.TICKCOLOR: tick_color_enum.GREEN},
            order_forward_enum.MIDDLE: {tick_type_key_enum.TICKTYPE: tick_type_enum.EXCHANGEUNKOWN,
                                        tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE}
        },
    open_interest_delta_forward_enum.OPENFWDOUBLE:
        {
            order_forward_enum.UP: {tick_type_key_enum.TICKTYPE: tick_type_enum.OPENDOUBLE,
                                    tick_type_key_enum.TICKCOLOR: tick_color_enum.RED},
            order_forward_enum.DOWN: {tick_type_key_enum.TICKTYPE: tick_type_enum.OPENDOUBLE,
                                      tick_type_key_enum.TICKCOLOR: tick_color_enum.GREEN},
            order_forward_enum.MIDDLE: {tick_type_key_enum.TICKTYPE: tick_type_enum.OPENDOUBLE,
                                        tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE}
        },
    open_interest_delta_forward_enum.OPEN:
        {
            order_forward_enum.UP: {tick_type_key_enum.TICKTYPE: tick_type_enum.OPENLONG,
                                    tick_type_key_enum.TICKCOLOR: tick_color_enum.RED},
            order_forward_enum.DOWN: {tick_type_key_enum.TICKTYPE: tick_type_enum.OPENSHORT,
                                      tick_type_key_enum.TICKCOLOR: tick_color_enum.GREEN},
            order_forward_enum.MIDDLE: {tick_type_key_enum.TICKTYPE: tick_type_enum.OPENUNKOWN,
                                        tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE}
        },
    open_interest_delta_forward_enum.CLOSEFWDOUBLE:
        {
            order_forward_enum.UP: {tick_type_key_enum.TICKTYPE: tick_type_enum.CLOSEDOUBLE,
                                    tick_type_key_enum.TICKCOLOR: tick_color_enum.RED},
            order_forward_enum.DOWN: {tick_type_key_enum.TICKTYPE: tick_type_enum.CLOSEDOUBLE,
                                      tick_type_key_enum.TICKCOLOR: tick_color_enum.GREEN},
            order_forward_enum.MIDDLE: {tick_type_key_enum.TICKTYPE: tick_type_enum.CLOSEDOUBLE,
                                        tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE}
        },
    open_interest_delta_forward_enum.CLOSE:
        {
            order_forward_enum.UP: {tick_type_key_enum.TICKTYPE: tick_type_enum.CLOSESHORT,
                                    tick_type_key_enum.TICKCOLOR: tick_color_enum.RED},
            order_forward_enum.DOWN: {tick_type_key_enum.TICKTYPE: tick_type_enum.CLOSELONG,
                                      tick_type_key_enum.TICKCOLOR: tick_color_enum.GREEN},
            order_forward_enum.MIDDLE: {tick_type_key_enum.TICKTYPE: tick_type_enum.CLOSEUNKOWN,
                                        tick_type_key_enum.TICKCOLOR: tick_color_enum.WHITE}
        },
}

# 只与计算对手单的组成相关，只有4种tick类型才需要计算对手单的组成
handicap_dict = {tick_type_enum.OPENLONG: {opponent_key_enum.OPPOSITE: tick_type_enum.CLOSELONG,
                                           opponent_key_enum.SIMILAR: tick_type_enum.OPENSHORT},
                 tick_type_enum.OPENSHORT: {opponent_key_enum.OPPOSITE: tick_type_enum.CLOSESHORT,
                                            opponent_key_enum.SIMILAR: tick_type_enum.OPENLONG},
                 tick_type_enum.CLOSELONG: {opponent_key_enum.OPPOSITE: tick_type_enum.OPENLONG,
                                            opponent_key_enum.SIMILAR: tick_type_enum.CLOSESHORT},
                 tick_type_enum.CLOSESHORT: {opponent_key_enum.OPPOSITE: tick_type_enum.OPENSHORT,
                                             opponent_key_enum.SIMILAR: tick_type_enum.CLOSELONG}
                 }


########################################################################
class TickAnalysis(MdApi):
    """测试用实例"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(TickAnalysis, self).__init__()
        self.PreDepthMarketData = None

    # ----------------------------------------------------------------------
    @simple_log
    def onFrontConnected(self):
        """服务器连接"""
        pass

    # ----------------------------------------------------------------------
    @simple_log
    def onFrontDisconnected(self, n):
        """服务器断开"""
        print n

    # ----------------------------------------------------------------------
    @simple_log
    def onHeartBeatWarning(self, n):
        """心跳报警"""
        print n

    # ----------------------------------------------------------------------
    @simple_log
    def onRspError(self, error, n, last):
        """错误"""
        print_dict(error)

    @simple_log
    # ----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        print_dict(data)
        print_dict(error)

    # ----------------------------------------------------------------------
    @simple_log
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        print_dict(data)
        print_dict(error)

    # ----------------------------------------------------------------------
    @simple_log
    def onRspSubMarketData(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(data)
        print_dict(error)

    # ----------------------------------------------------------------------
    @simple_log
    def onRspUnSubMarketData(self, data, error, n, last):
        """退订合约回报"""
        print_dict(data)
        print_dict(error)

        # ----------------------------------------------------------------------

    """
    struct CThostFtdcDepthMarketDataField
    {
     ///交易日
     TThostFtdcDateType TradingDay;
     ///合约代码
     TThostFtdcInstrumentIDType InstrumentID;
     ///交易所代码
     TThostFtdcExchangeIDType ExchangeID;
     ///合约在交易所的代码
     TThostFtdcExchangeInstIDType ExchangeInstID;
     ///最新价
     TThostFtdcPriceType LastPrice;
     ///上次结算价
     TThostFtdcPriceType PreSettlementPrice;
     ///昨收盘
     TThostFtdcPriceType PreClosePrice;
     ///昨持仓量
     TThostFtdcLargeVolumeType PreOpenInterest;
     ///今开盘
     TThostFtdcPriceType OpenPrice;
     ///最高价
     TThostFtdcPriceType HighestPrice;
     ///最低价
     TThostFtdcPriceType LowestPrice;
     ///数量
     TThostFtdcVolumeType Volume;
     ///成交金额
     TThostFtdcMoneyType Turnover;
     ///持仓量
     TThostFtdcLargeVolumeType OpenInterest;
     ///今收盘
     TThostFtdcPriceType ClosePrice;
     ///本次结算价
     TThostFtdcPriceType SettlementPrice;
     ///涨停板价
     TThostFtdcPriceType UpperLimitPrice;
     ///跌停板价
     TThostFtdcPriceType LowerLimitPrice;
     ///昨虚实度
     TThostFtdcRatioType PreDelta;
     ///今虚实度
     TThostFtdcRatioType CurrDelta;
     ///最后修改时间
     TThostFtdcTimeType UpdateTime;
     ///最后修改毫秒
     TThostFtdcMillisecType UpdateMillisec;
     ///申买价一
     TThostFtdcPriceType BidPrice1;
     ///申买量一
     TThostFtdcVolumeType BidVolume1;
     ///申卖价一
     TThostFtdcPriceType AskPrice1;
     ///申卖量一
     TThostFtdcVolumeType AskVolume1;
     ///申买价二
     TThostFtdcPriceType BidPrice2;
     ///申买量二
     TThostFtdcVolumeType BidVolume2;
     ///申卖价二
     TThostFtdcPriceType AskPrice2;
     ///申卖量二
     TThostFtdcVolumeType AskVolume2;
     ///申买价三
     TThostFtdcPriceType BidPrice3;
     ///申买量三
     TThostFtdcVolumeType BidVolume3;
     ///申卖价三
     TThostFtdcPriceType AskPrice3;
     ///申卖量三
     TThostFtdcVolumeType AskVolume3;
     ///申买价四
     TThostFtdcPriceType BidPrice4;
     ///申买量四
     TThostFtdcVolumeType BidVolume4;
     ///申卖价四
     TThostFtdcPriceType AskPrice4;
     ///申卖量四
     TThostFtdcVolumeType AskVolume4;
     ///申买价五
     TThostFtdcPriceType BidPrice5;
     ///申买量五
     TThostFtdcVolumeType BidVolume5;
     ///申卖价五
     TThostFtdcPriceType AskPrice5;
     ///申卖量五
     TThostFtdcVolumeType AskVolume5;
     ///当日均价
     TThostFtdcPriceType	AveragePrice;
    };
    """

    # @simple_log
    def onRtnDepthMarketData(self, data):
        """行情持续推送"""
        # print_dict(data)
        """
        输入：tick数据
        输出：
        时间，价格，成交，增仓，性质，颜色
        对手单逆向性质，对手单逆向数量
        对手单同向性质，对手单同向数量

        有8种盘口的tick性质，商品期货都是双边统计
        多开(OpenLong)，空开(OpenShort)，双开(OpenDouble)
        多平(CloseLong)，空平(CloseShort)，双平(CloseDouble)
        多换(ExchangeLong)，空换(ExchangeShort)
        对于仓位的变化来讲分三类：开仓，平仓，换仓
        开仓：持仓量增加
        平仓：持仓量减少
        换仓：持仓量不变
        """
        if self.PreDepthMarketData is not None:

            # 计算两tick之间的差值
            ask_price_delta = self.PreDepthMarketData['AskPrice1'] - data['AskPrice1']
            ask_volume_delta = self.PreDepthMarketData['AskVolume1'] - data['AskVolume1']
            bid_price_delta = self.PreDepthMarketData['BidPrice1'] - data['BidPrice1']
            bid_volume_delta = self.PreDepthMarketData['BidVolume1'] - data['BidVolume1']
            last_price_delta = self.PreDepthMarketData['LastPrice'] - data['LastPrice']
            volume_delta = data['Volume'] - self.PreDepthMarketData['Volume']
            open_interest_delta = int(data['OpenInterest'] - self.PreDepthMarketData['OpenInterest'])

            # 编移量的显示字符串
            ask_price_delta_str = self.get_delta_str(self.PreDepthMarketData['AskPrice1'], data['AskPrice1'])
            ask_volume_delta_str = self.get_delta_str(self.PreDepthMarketData['AskVolume1'], data['AskVolume1'])
            bid_price_delta_str = self.get_delta_str(self.PreDepthMarketData['BidPrice1'], data['BidPrice1'])
            bid_volume_delta_str = self.get_delta_str(self.PreDepthMarketData['BidVolume1'], data['BidVolume1'])
            last_price_delta_str = self.get_delta_str(self.PreDepthMarketData['LastPrice'], data['LastPrice'])

            # 如果ask或者bid价格对比上一个tick都发生了变化则不显示价格变化幅度
            if ask_price_delta != 0:
                ask_volume_delta_str = ''
            if bid_price_delta != 0:
                bid_volume_delta_str = ''

            # input1 计算订单是在ask范围内成交还是在bid范围内成交
            order_forward = TickAnalysis.get_order_forward(data["LastPrice"], data["AskPrice1"], data["BidPrice1"],
                                                           self.PreDepthMarketData["LastPrice"],
                                                           self.PreDepthMarketData["AskPrice1"],
                                                           self.PreDepthMarketData["BidPrice1"])
            # input2 计算仓位变化方向
            open_interest_delta_forward = TickAnalysis.get_open_interest_delta_forward(open_interest_delta,
                                                                                       volume_delta)

            # f(input1,input2) = output1 根据成交区域和仓位变化方向计算出tick的类型
            tick_type_dict = tick_type_cal_dict[open_interest_delta_forward][order_forward]

            if open_interest_delta_forward != open_interest_delta_forward_enum.NONE:
                # 输出相关变量
                print "Ask\t" + str(data['AskPrice1']) + ask_price_delta_str + "\t" + str(
                    data['AskVolume1']) + ask_volume_delta_str \
                      + "\tBid\t" + str(data['BidPrice1']) + bid_price_delta_str + "\t" + str(
                    data['BidVolume1']) + bid_volume_delta_str

                print str(data['UpdateTime']) + "." + str(data['UpdateMillisec']) \
                      + "\t" + str(data['LastPrice']) + last_price_delta_str \
                      + "\t成交 " + str(volume_delta) \
                      + "\t增仓 " + str(open_interest_delta) \
                      + "\t" + tick_type_str_dict[tick_type_dict[tick_type_key_enum.TICKTYPE]] \
                      + "\t" + tick_type_str_dict[tick_type_dict[tick_type_key_enum.TICKCOLOR]]

                if tick_type_dict[tick_type_key_enum.TICKTYPE] in handicap_dict.keys():
                    order_opposite, order_similar = TickAnalysis.get_order_combination(open_interest_delta,
                                                                                       volume_delta)
                    print "对手单：" + tick_type_str_dict[
                              handicap_dict[tick_type_dict[tick_type_key_enum.TICKTYPE]][opponent_key_enum.OPPOSITE]] \
                          + " " + str(order_opposite) \
                          + "\t" + tick_type_str_dict[
                              handicap_dict[tick_type_dict[tick_type_key_enum.TICKTYPE]][opponent_key_enum.SIMILAR]] \
                          + " " + str(order_similar)

                print '--------------------------------------'

        self.PreDepthMarketData = data

    # -----------------------------------------------------------------------
    @staticmethod
    def float_smaller_equal(smaller, bigger):
        return TickAnalysis.float_bigger_equal(bigger, smaller)

    @staticmethod
    def float_bigger_equal(bigger, smaller):
        """ float型的数不能直接相等
        http://www.sharejs.com/codes/python/223
        """
        ret = False
        if abs(bigger - smaller) < 0.00001:
            ret = True
        elif bigger > smaller:
            ret = True

        return ret

    # ----------------------------------------------------------------------
    @staticmethod
    def get_open_interest_delta_forward(open_interest_delta, volume_delta):
        """根据成交量的差和持仓量的差来获取仓位变化的方向
            return: open_interest_delta_forward_enum
        """
        if open_interest_delta == 0 and volume_delta == 0:
            local_open_interest_delta_forward = open_interest_delta_forward_enum.NONE
        elif open_interest_delta == 0 and volume_delta > 0:
            local_open_interest_delta_forward = open_interest_delta_forward_enum.EXCHANGE
        elif open_interest_delta > 0:
            if open_interest_delta - volume_delta == 0:
                local_open_interest_delta_forward = open_interest_delta_forward_enum.OPENFWDOUBLE
            else:
                local_open_interest_delta_forward = open_interest_delta_forward_enum.OPEN
        elif open_interest_delta < 0:
            if open_interest_delta + volume_delta == 0:
                local_open_interest_delta_forward = open_interest_delta_forward_enum.CLOSEFWDOUBLE
            else:
                local_open_interest_delta_forward = open_interest_delta_forward_enum.CLOSE
        return local_open_interest_delta_forward

    # ----------------------------------------------------------------------
    @staticmethod
    def get_order_forward(last_price, ask_price1, bid_price1, pre_last_price, pre_ask_price1, pre_bid_price1):
        """获取成交的区域，根据当前tick的成交价和上个tick的ask和bid价格进行比对
           return: order_forward_enum
        """
        if TickAnalysis.float_bigger_equal(last_price, pre_ask_price1):
            local_order_forward = order_forward_enum.UP
        elif TickAnalysis.float_smaller_equal(last_price, pre_bid_price1):
            local_order_forward = order_forward_enum.DOWN
        else:
            if TickAnalysis.float_bigger_equal(last_price, ask_price1):
                local_order_forward = order_forward_enum.UP
            elif TickAnalysis.float_smaller_equal(last_price, bid_price1):
                local_order_forward = order_forward_enum.DOWN
            else:
                local_order_forward = order_forward_enum.MIDDLE

        return local_order_forward

    # ----------------------------------------------------------------------
    @staticmethod
    def get_order_combination(open_interest_delta, volume_delta):
        """根据成交量变化和持仓量的变化计算出对手单的组合

            仓位变化方向相反的单
                order_opposite
            仓位变化方向相同的单
                order_similar

        """
        open_interest_delta = open_interest_delta if open_interest_delta > 0 else -open_interest_delta
        volume_delta_single_side = volume_delta / 2.0
        open_close_delta = open_interest_delta - volume_delta_single_side + 0.0
        order_similar = volume_delta_single_side / 2 + open_close_delta / 2
        order_opposite = volume_delta_single_side / 2 - open_close_delta / 2

        return int(order_opposite), int(order_similar)

    @staticmethod
    def get_delta_str(pre, data):
        offset_str = ''
        if data > pre:
            offset_str = '(+' + str(data - pre) + ")"
        elif data < pre:
            offset_str = '(-' + str(pre - data) + ")"
        else:
            pass
        return offset_str

    # ----------------------------------------------------------------------
    def CompareDepthMarketData(self, data):
        """做tick数据的前后比较"""
        if self.PreDepthMarketData is not None:
            for key, value in self.PreDepthMarketData.items():
                if value != data[key]:
                    print key + ': pre->' + str(value) + " now->" + str(data[key])
        self.PreDepthMarketData = data

    # ----------------------------------------------------------------------
    @simple_log
    def onRspSubForQuoteRsp(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(data)
        print_dict(error)

    # ----------------------------------------------------------------------
    @simple_log
    def onRspUnSubForQuoteRsp(self, data, error, n, last):
        """退订合约回报"""
        print_dict(data)
        print_dict(error)

        # ----------------------------------------------------------------------

    '''
    ///发给做市商的询价请求
    struct CThostFtdcForQuoteRspField
    {
        ///交易日
        TThostFtdcDateType	TradingDay;
        ///合约代码
        TThostFtdcInstrumentIDType	InstrumentID;
        ///询价编号
        TThostFtdcOrderSysIDType	ForQuoteSysID;
        ///询价时间
        TThostFtdcTimeType	ForQuoteTime;
        ///业务日期
        TThostFtdcDateType	ActionDay;
        ///交易所代码
        TThostFtdcExchangeIDType	ExchangeID;
    };
    '''

    @simple_log
    def onRtnForQuoteRsp(self, data):
        """行情推送"""
        print_dict(data)

        # ----------------------------------------------------------------------


def main():
    """主测试函数，出现堵塞时可以考虑使用sleep"""
    reqid = 0

    # 创建Qt应用对象，用于事件循环
    app = QtGui.QApplication(sys.argv)

    # 创建API对象
    api = TickAnalysis()

    # 在C++环境中创建MdApi对象，传入参数是希望用来保存.con文件的地址
    api.createFtdcMdApi('')

    # 注册前置机地址
    # api.registerFront("tcp://qqfz-md1.ctp.shcifco.com:32313")
    api.registerFront("tcp://180.168.212.228:41213")

    # 初始化api，连接前置机
    api.init()
    sleep(0.5)

    # 登陆
    loginReq = {}  # 创建一个空字典
    loginReq['UserID'] = ''  # 参数作为字典键值的方式传入
    loginReq['Password'] = ''  # 键名和C++中的结构体成员名对应
    loginReq['BrokerID'] = '9999'
    reqid = reqid + 1  # 请求数必须保持唯一性
    i = api.reqUserLogin(loginReq, 1)
    sleep(0.5)

    ## 登出，测试出错（无此功能）
    # reqid = reqid + 1
    # i = api.reqUserLogout({}, 1)
    # sleep(0.5)

    ## 安全退出，测试通过
    # i = api.exit()

    ## 获取交易日，目前输出为空
    day = api.getTradingDay()
    print 'Trading Day is:' + str(day)
    sleep(0.5)

    ## 订阅合约，测试通过
    i = api.subscribeMarketData('j1705')

    ## 退订合约，测试通过
    # i = api.unSubscribeMarketData('IF1505')

    # 订阅询价，测试通过
    # i = api.subscribeForQuoteRsp('IO1504-C-3900')

    # 退订询价，测试通过
    # i = api.unSubscribeForQuoteRsp('IO1504-C-3900')

    # 连续运行，用于输出行情
    app.exec_()


if __name__ == '__main__':
    main()
