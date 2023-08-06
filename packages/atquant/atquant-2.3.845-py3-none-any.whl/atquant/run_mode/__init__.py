# -*- coding: utf-8 -*-
from . import trader_run_back_test
from . import trader_run_real_trade
from . import trader_run_replay


__all__ = [
    "traderRunBacktestV2",
    "traderRunRealTradeV2",
    "traderRunReplayV2",
]


# noinspection PyPep8Naming
def traderRunBacktestV2(StrategyName, TradeFun, varFunParameter, AccountList, TargetList, KFrequency, KFreNum, BeginDate, EndDate, FQ, *args):
    '''
    实现策略的回测
    
    :param StrategyName: str, 策略名称
    :param TradeFun: types.FunctionType，策略函数
    :param varFunParameter: tuple，策略函数中用到的参数
    :param AccountList: list，账户列表
    :param TargetList: list of dict，标的列表词典，词典具体结构如下:
    ::
    
        Market: str,市场名称，如:'CFFEX'
        Code: str, 交易品种代码，如'IF0000'
    ..
    :param KFrequency: str，K线的时间级别，如: 'tick','sec','min','day','week','month','year'
    :param KFreNum: int，K线的频数
    :param BeginDate: int，开始日期，如：20180115
    :param EndDate: int，结束日期，如：20180215
    :param FQ: str, 复权类型，'NA' 为不复权，'FWard' 向前复权，'BWard' 向后复权
    :param args: 支持的参数：
    ::
    
        AlgoTradeFun: 算法交易函数
        varAlgoFunParameter: 算法交易函数的参数
    ..
    :return: 
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        from atquant import run_mode
        
        len1 = 5
        len2 = 20
        shareNum = 2
        stoploss = 0.5
        stopprofit = 1
        trailinggap = 0.5
        AccountList = ['FutureBackReplay']
        TargetList = [{'Market': 'SHFE', 'Code': 'RB0000'},
                    {'Market': 'CFFEX', 'Code': 'IF0000'}]
        StrategyName = 'BackTestTwoLines'
        api.traderSetBacktest(1e7, 2.6e-5, 0.02, 0, 1, 0, 0)
        # TwoLines, (len1, len2, shareNum, stoploss, stopprofit, trailinggap) 为你写的函数,以及函数的参数
        run_mode.traderRunBacktestV2(StrategyName, TwoLines, (len1, len2, shareNum, stoploss, stopprofit, trailinggap),
                                 AccountList, TargetList, "min", 1, 20171220, 20171225, 'FWard')
    '''

    return trader_run_back_test.traderRunBacktestV2(StrategyName, TradeFun, varFunParameter, AccountList, TargetList, KFrequency, KFreNum, BeginDate, EndDate, FQ, *args)


# noinspection PyPep8Naming
def traderRunRealTradeV2(StrategyName, TradeFun, varFunParameter, AccountList, TargetList, KFrequency, KFreNum, BeginDate, FQ, *args):
    '''
    实现策略的实盘交易，只支持单一策略
    
    :param StrategyName: str, 策略名称
    :param TradeFun: types.FunctionType，策略函数
    :param varFunParameter: tuple，策略函数中用到的参数
    :param AccountList: list，账户列表
    :param TargetList: list of dict，标的列表词典，词典具体结构如下:
    ::
    
        Market: str,市场名称，如:'CFFEX'
        Code: str, 交易品种代码，如'IF0000'
    ..
    :param KFrequency: str，K线的时间级别，如: 'tick','sec','min','day','week','month','year'
    :param KFreNum: int，K线的频数
    :param BeginDate: int，开始日期，如：20180115
    :param FQ: str, 复权类型，'NA' 为不复权，'FWard' 向前复权，'BWard' 向后复权
    :param args: 支持的参数：
    ::
    
        AlgoTradeFun: 算法交易函数
        varAlgoFunParameter: 算法交易函数的参数
    ..
    :return: 
    '''

    return trader_run_real_trade.traderRunRealTradeV2(StrategyName, TradeFun, varFunParameter, AccountList, TargetList, KFrequency, KFreNum, BeginDate, FQ, *args)


# noinspection PyPep8Naming
def traderRunReplayV2(StrategyName, TradeFun, varFunParameter, AccountList, TargetList, KFrequency, KFreNum, BeginDate, RepalyDate, FQ, AlgoTradeFun=None, varAlgoFunParameter=None):
    '''
    实现策略的回放
    
    :param StrategyName: str, 策略名称
    :param TradeFun: types.FunctionType，策略函数
    :param varFunParameter: tuple，策略函数中用到的参数
    :param AccountList: list，账户列表
    :param TargetList: list of dict，标的列表词典，词典具体结构如下:
    ::
    
        Market: str,市场名称，如:'CFFEX'
        Code: str, 交易品种代码，如'IF0000'
    ..
    :param KFrequency: str，K线的时间级别，如: 'tick','sec','min','day','week','month','year'
    :param KFreNum: int，K线的频数
    :param BeginDate: int，开始日期，如：20180115
    :param RepalyDate: int, 回放日期
    :param FQ: str, 复权类型，'NA' 为不复权，'FWard' 向前复权，'BWard' 向后复权
    :param AlgoTradeFun: FunctionType,算法交易函数
    :param varAlgoFunParameter: 算法交易函数的参数
    :return: 
    '''

    return trader_run_replay.traderRunReplayV2(StrategyName, TradeFun, varFunParameter, AccountList, TargetList, KFrequency, KFreNum, BeginDate, RepalyDate, FQ, AlgoTradeFun, varAlgoFunParameter)
