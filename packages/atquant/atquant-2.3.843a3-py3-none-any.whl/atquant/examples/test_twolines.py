# -*- coding: utf-8 -*-


import numpy as np

from atquant import api
from atquant import run_mode

g_idxK = 0
g_idxUD = 0
g_idxMean = 0
dtMean1_old = 0
dtMean2_old = 0


# noinspection PyPep8Naming
def MyMean(cellPar, bpPFCell):
    idxK = cellPar[0]
    len1 = cellPar[1]
    len2 = cellPar[2]
    targetNum = np.shape(idxK)
    targetNum = targetNum[0]
    value = np.ones((targetNum, 1)) * float('nan')
    for i in range(targetNum):
        regKMatrix = api.traderGetRegKData(np.array([idxK[i, :]]), max(len1, len2), True, bpPFCell)
        KLen = np.size(regKMatrix, axis=1)
        if KLen >= max(len1, len2):
            # 这里可以根据用户自己的需求进行精度控制
            dtMean1 = np.mean(regKMatrix[4, -1 - len1 + 1:], dtype=np.float64)
            dtMean2 = np.mean(regKMatrix[4, -1 - len2 + 1:], dtype=np.float64)
            if dtMean1 - dtMean2 > 0.000001:
                value[i] = 1
            if dtMean2 - dtMean1 > 0.000001:
                value[i] = 2
    return value


# noinspection PyPep8Naming
def TwoLines(bInit, bDayBegin, cellPar):
    global g_idxK
    global g_idxUD
    global g_idxMean
    len1 = cellPar[0]
    len2 = cellPar[1]
    shareNum = cellPar[2]
    stoploss = cellPar[3]
    stopprofit = cellPar[4]
    trailinggap = cellPar[5]
    if bInit:
        g_idxK = api.traderRegKData('min', 5)
        g_idxMean = api.traderRegUserIndi(MyMean, (g_idxK, len1, len2))
    else:
        (BarNumber, BarTime) = api.traderGetCurrentBarV2()
        # python是从0开始索引barNumber的，因此想要取第40根bar要用39
        if BarNumber < (40 - 1):
            return

        targetList = api.traderGetTargetList()
        TLen = len(targetList)
        dtValue = api.traderGetRegUserIndi(g_idxMean, 1)
        Position, _, _ = api.traderGetAccountPositionV2(0, np.arange(TLen))
        for i in range(TLen):
            if Position[0, i] <= 0 and dtValue[i] == 1:
                # 此处注意Python是从0开始索引的，如果要使用第一个账号请输入0
                orderID1 = api.traderBuyV2(0, i, shareNum, 0, 'market', 'buy1')
            if Position[0, i] >= 0 and dtValue[i] == 2:
                orderID2 = api.traderSellShortV2(0, i, shareNum, 0, 'market', 'sell1')


def testRunRealTrade():
    len1 = 5
    len2 = 20
    shareNum = 2
    stoploss = 0.5
    stopprofit = 1
    trailinggap = 0.5
    AccountList = ['FutureSimAcc02', 'OptionSimAcc02']
    TargetList = [
        {'Market': 'shfe', 'Code': 'ru0000'},
        {'Market': 'CFFEX', 'Code': 'IH0000'},
        {'Market': 'szse', 'Code': '000004'},
    ]
    KFrequency = "min"
    KFreNum = 10
    EndDate = 20180308
    StrategyName = 'MyFirstStrategy'
    api.traderSetBacktest(10000000, 0.000026, 0.02, 0, 1, 0, 0)
    run_mode.traderRunRealTradeV2(StrategyName, TwoLines, (len1, len2, shareNum, stoploss, stopprofit, trailinggap),
                                  AccountList, TargetList, KFrequency, KFreNum, EndDate, 'FWard')


def testRunBacktest():
    len1 = 5
    len2 = 20
    shareNum = 2
    stoploss = 0.5
    stopprofit = 1
    trailinggap = 0.5

    AccountList = ['FutureBackReplay']
    TargetList = [
        {'Market': 'shfe', 'Code': 'ru0000'},
        {'Market': 'CFFEX', 'Code': 'IH0000'},
        {'Market': 'cffex', 'Code': 'if0000'},
    ]
    KFrequency = "min"
    KFreNum = 1
    BeginDate = 20170101
    EndDate = 20170128
    StrategyName = 'BackTestTwoLines'
    api.traderSetBacktest(10000000, 0.000026, 0.02, 0, 1, 0, 0)
    run_mode.traderRunBacktestV2(StrategyName, TwoLines, (len1, len2, shareNum, stoploss, stopprofit, trailinggap),
                                 AccountList, TargetList, KFrequency, KFreNum, BeginDate, EndDate, 'FWard')


# 这里由于需要Windows下的多进程因此调用traderRunBacktestV2必须是从main函数进入
if __name__ == '__main__':
    testRunRealTrade()
