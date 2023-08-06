# -*- coding: utf-8 -*-

import sys

sys.path.append("..")
from . import init_set

__all__ = [
    "traderPutLog",
    "traderGetFutureInfo",
    "traderGetFutureInfoV2",
    "traderGetTradingTime",
    "traderAppendKDataScope",
    "traderSetBacktest",
    "traderSetParalMode",
    "traderRegKData",
    "traderGetKData",
    "traderRegUserIndi",
    "traderGetRegKData",
    "traderGetCurrentBarV2",
    "traderGetTargetList",
    "traderGetRegUserIndi",
    "traderGetAccountPositionV2",
    "traderBuyV2",
    "traderSellShortV2",
    "traderPositionToV2",
    "traderGetAccountPositionDirV2",
    "traderConfigTo",
    "traderGetAccountConfig",
    "traderGetCodeList",
    "traderSetMarketOrderHoldingType",
    "traderGetTargetInfoV2",
    "traderGetTargetInfo",
    "traderGetMainContract",
]


# noinspection PyPep8Naming
# @trace_time
def traderPutLog(Handle, StrategyName, Log):
    '''
    构造 log 信息发送至 AT
    
    :param Handle: int, 账户句柄 
    :param StrategyName: str, 策略名称
    :param Log: str, 日志信息
    :return: None
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        # 在AutoTrader 连接之后
        api.traderPutLog(0,'myFirstStategy','get history data')
    '''

    return init_set.traderPutLog(Handle, StrategyName, Log)


# noinspection PyPep8Naming
# @trace_time
def traderSetMarketOrderHoldingType(MarketOrderHolding):
    '''
    设置市价单保持状态。
    
    :param MarketOrderHolding: bool, 当一下根bar成交量为0时，True,则在成交量等于0时撤单，否则为保持状态
    :return: None
    '''

    return init_set.traderSetMarketOrderHoldingType(MarketOrderHolding)


# noinspection PyPep8Naming
# @trace_time
def traderGetFutureInfo(Market, Code):
    '''
    获取期货信息, 获取股票信息

    :param Market: str,市场类型,允许值如下：
    ::

        'SZSE’：深圳股票
        'SSE'：上海股票
        'SHFE'：上海期货
        'DCE' ：大连商品
        'CZCE'：郑州商品
        'CFFEX'：中金所
    ..
    :param Code: str, 交易品种代码，字符串格式，如'IF0000'
    :return: info, dict,主要包含以下:
    ::

        Name: 对应的品种代码
        LastTD: 最后交易日
        Multiple:合约乘数
        MinMove:最小变动单位
        TradingFeeOpen:开仓手续费率
        TradingFeeClose:平仓手续费率
        TradingFeeCloseToday:当日平仓手续费
        LongMargin:多方保证金率
        ShortMargin:空方保证金率
    ..
    
    :Example: 只能在策略运行时进行调用，访问数据可以采用以下形式
    .. code-block:: python
        :linenos:
        
        from atquant import api
        print(api.traderGetFutureInfo('SHFE', 'ru0000'))
    
    '''

    return init_set.traderGetFutureInfo(Market, Code)


# noinspection PyPep8Naming
# @trace_time
def traderGetFutureInfoV2(TargetIdxA):
    '''
    获取期货信息，获取股票信息
    
    :param TargetIdxA: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray, 交易标的索引序列号
    :return: pandas.DataFrame 主要包含如下信息:
    
    ::
    
        Multiple:               合约乘数
        MinMove:                最小变动单位
        TradingFeeOpen:         开仓手续费率
        TradingFeeClose:        平仓手续费率，（平昨或者统一概括）
        TradingFeeCloseToday:   当日平仓手续费
        LongMargin:             多方保证金率
        ShortMargin:            空方保证金率
    ..
    
    :Example: 
    .. code-block:: python
        :linenos:
        
        # 只能在策略运行时进行调用，访问数据可以采用以下形式:
        import pandas as pd
        from atquant import api
        # 需要注册相关标的后方可使用:
        df = api.traderGetFutureInfoV2([0])
    '''

    return init_set.traderGetFutureInfoV2(TargetIdxA)


# noinspection PyPep8Naming
# @trace_time
def traderGetTradingTime(TargetList, freq, BeginDay, EndDay):
    '''
    获取交易时间。
    
    :param TargetList: list, 策略标的词典列表,词典包含:
    ::
    
        'Market': str, 市场类型
        'Code':   str, 交易品种代码
    ..
    :param freq: str, 返回的时间精细级别, 如: 'tick','sec','min','day','week','month','year'
    :param BeginDay: int, 开始日期, 如20170216
    :param EndDay: int, 结束日期, 如20170222
    :return: Time,DayPos
    ::
    
       Time:    numpy.ndarry(N*1), 时间点, matlab 浮点型数字
       DayPos:  numpy.ndarry(N*1), 天标志
    ..
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        TargetList = [{'Market': 'shfe', 'Code': 'ru0000'},{'Market': 'CFFEX', 'Code': 'IF0000'}]
        (Time, DayPos) = api.traderGetTradingTime(TargetList, 'min', 20170216, 20170217)
        
        >>> Time
        [736741.8756944444, 736741.87638888892, …, 736743.6243055556, 736743.625]
        >>> DayPos
        [1, 2,…, 389, 390]
    '''

    return init_set.traderGetTradingTime(TargetList, freq, BeginDay, EndDay)


# noinspection PyPep8Naming
# @trace_time
def traderGetTradingDays(BeginDay, EndDay):
    '''
    获取指定日期内，所有的交易日，如果endday为0，则返回从开始时间一直到最近一个交易日中间所有的交易日期
    
    :param BeginDay: 开始交易日期，整型日期，如: 20161201
    :param EndDay: 结束交易日期，整型日期，如: 20161220
    :return: Days: 交易时间，numpy.ndarray一维结构 
    :Example::
    .. code-block:: pyhton
        :linenos:
        
        from atquant Import api
        Days = api.traderGetTradingDays(20161201, 20161205)
        
        >>> Days
        [ 20161201.  20161202.  20161205.]
    '''

    return init_set.traderGetTradingDays(BeginDay, EndDay)


# noinspection PyPep8Naming
# @trace_time
def traderAppendKDataScope(KFrequency, DateSpan, FillUp):
    '''
    扩充低频数据。

    :param KFrequency: str, K线类型，如min，day 
    :param DateSpan: int, 数量
    :param FillUp: bool, 是否需要填充序列
    :return: None
    :Example:
    .. code-block:: python
        :linenos:
        
        # 回测开始时点向前扩充200天的日线数据
        from atquant import api
        api. traderAppendKDataScope (day, 200,True)
    '''

    return init_set.traderAppendKDataScope(KFrequency, DateSpan, FillUp)


# noinspection PyPep8Naming
# @trace_time
def traderSetBacktest(InitialCash, Costfee, Rate, SlidePrice, *args):
    '''
    初始化信息设置，使用traderSetBacktest对回测过程中的各项配置提前赋值或选择。该函数仅限于期货策略使用，股票策略无需配置。
    
    :param InitialCash: int, 初始资本，默认为1000000
    :param Costfee: float, 手续费率，默认为0.0025
    :param Rate: float, 无风险利率，默认为0.02
    :param SlidePrice: float 滑价，默认为0
    :param args: 可选参数: 
    ::
    
       PriceLoc：int, 市价单成交位置:
            0-当前bar收盘价;
            1-下一个bar开盘价;
            2-下一个bar第二个tick;
            n-下一个bar第n个tick;
            默认为1，即下一个bar的开盘价;
       DealType：int, 市价单成交类型：
            0-成交价；
            1-对方最优价；
            2-己方最优价；
            默认0
       LimitType：int, 限价单成交方式：
            0-直接成交；
            1-下一个bar内没有该价格时，撤单处理；
            默认0
    ..
    :return: None
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        # 在回测时设置初始资本1000000元、手续费率0.0025、无风险利率0.02、滑价0、默认1下一个bar的开盘价、默认0成交价、默认0直接成交
        api.traderSetBacktest(1000000,0.0025,0.02,0,1,0,0)
    ..
    '''

    return init_set.traderSetBacktest(InitialCash, Costfee, Rate, SlidePrice, *args)


# noinspection PyPep8Naming
# @trace_time
def traderSetParalMode(bParalMode):
    '''
    设置是否使用并行模式
    
    :param bParalMode: bool,True 并行，False 非并行 
    :return: None
    '''

    return init_set.traderSetParalMode(bParalMode)


# noinspection PyPep8Naming
# @trace_time
def traderRegKData(KFrequency, KFreNum):
    '''
    注册数据。根据用户需求的频率及频数，返回A,B,C A为合并后的矩阵的索引，B为矩阵中具体数据的索引，C为数据刷新轴的索引
    
    :param KFrequency: str,如 min，day
    :param KFreNum: int,K线的频率
    :return: numpy.ndarray, N*3，N为Target数目
    '''

    return init_set.traderRegKData(KFrequency, KFreNum)


# noinspection PyPep8Naming
# @trace_time
def traderGetRegKData(Idx, length, FilledUp, *args):
    '''
    根据已注册的数据序列获取K线数据；可通过此函数获取该时段内重要的价量数据。

    :param Idx: numpy.asarray(N*3)支持的数据类型, 注册数据时返回的索引序列号。
    :param length: int, 序列长度。例120，表示返回从当前开始往前的120个数据序列。
    :param FilledUp: bool, 补齐类型，False表示不补齐，True为补齐。
    :param args: 函数固定结构，并行计算中的入参模式。有函数入参时必须将该参数入参。
    :return: numpy.ndarray。
    ::
    
        OutMatrix:返回K线数据价量的信息numpy二维数组，包含:
        第一行: time:时间列表，1×N double型数组，以Matlab日期数字形式存储。
        第二行: open:开盘价数据，1×N double型数组，每个元素对应time中时间点的开盘价。
        第三行: high:最高价数据，1×N double型数组，每个元素对应time中时间点的最高价。
        第四行 :low:最低价数据，1×N double型数组，每个元素对应time中时间点的最低价。
        第五行: close:收盘价数据，1×N double型数组，每个元素对应time中时间点的收盘价。
        第六行: volume:成交量数据，1×N double型数组，每个元素对应time中时间点的成交量。
        第七行: turnover:成交金额，1×N double型数组，每个元素对应time中时间点的换手率。
        第八行: openinterest:持仓量数据，1×N double型数组，每个元素对应time中时间点的持仓量
    ..
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        KIdx=api.traderRegKData(‘day’,5)
        # 以不补齐方式获取上述已注册数据,取出长度为10根bar
        KMatrix= traderGetRegKData(KIdx,10,false)
    '''

    return init_set.traderGetRegKData(Idx, length, FilledUp, *args)


# noinspection PyPep8Naming
# @trace_time
def traderGetKData(Market, Code, KFrequency, KFreNum, BeginDate, EndDate, FilledUp, FQ):
    '''
    根据起止时间点提取K线数据；可通过此函数获取该时段内重要的价量数据

    :param Market: str,市场类型,允许值如下：
    ::

        'SZSE’：深圳股票
        'SSE'：上海股票
        'SHFE'：上海期货
        'DCE' ：大连商品
        'CZCE'：郑州商品
        'CFFEX'：中金所
    ..
    :param Code: str, 交易品种代码，如'IF0000'
    :param KFrequency: str，K线的时间级别，如: 'tick','sec','min','day','week','month','year'
    :param KFreNum: int，K线的频数
    :param BeginDate: int，开始日期，如：20180115
    :param EndDate: int，结束日期，如：20180215
    :param FilledUp: bool, 补齐类型，False表示不补齐，True为补齐
    :param FQ: str, 复权类型，'NA' 为不复权，'FWard' 向前复权，'BWard' 向后复权
    :return: time,open,high,low,close,volume,turnover,openinterest
    ::

        time：时间列表，N×1 double型数组，以Matlab日期数字形式存储。
        open：开盘价数据，N×1 double型数组，每个元素对应time中时间点的开盘价。
        high：最高价数据，N×1 double型数组，每个元素对应time中时间点的最高价。
        low：最低价数据，N×1 double型数组，每个元素对应time中时间点的最低价。
        close：收盘价数据，N×1 double型数组，每个元素对应time中时间点的收盘价。
        volume：成交量数据，N×1 double型数组，每个元素对应time中时间点的成交量。
        turnover：成交金额，N×1 double型数组，每个元素对应time中时间点的换手率。
        openinterest：持仓量数据，N×1 double型数组，每个元素对应time中时间点的持仓量。  
    ..
    :Example:
    .. code-block:: python
        :linenos:

        from atquant import api
        # 获取代码为IF0000的股指期货主力合约在2014年的1分钟，补齐的不复权K线数据
        [time,open,high,low,close,volume,turnover,openinterest]=api.traderGetKData('CFFEX', 'IF0000', 'min', 1, 20140101, 20141231, True, 'NA')
        # 获得代码为000002的股票的2014年6、7月份不补齐的向前复权的1日K线数据
        [time,open,high,low,close,volume,turnover,openinterest]=api.traderGetKData('SZSE', '000002', 'day', 1, 20140601, 20140731, False, 'FWard')
    '''

    return init_set.traderGetKData(Market, Code, KFrequency, KFreNum, BeginDate, EndDate, FilledUp, FQ)


# noinspection PyPep8Naming
# @trace_time
def traderGetTickDataV2(TargetIdx, Date, FQ):
    '''
    获取时间点Tick行情数据
    
    :param TargetIdx: int, 标的索引,从0开始
    :param Date: int，具体日期。如: 20150501
    :param FQ: str, 复权类型。不复权'NA'，前复权'FWard',后复权'BWard'
    :return: 
        Time：时间列表，N×1 double型数组，以Matlab 日期数字形式存储。
        Price：价格，此处为成交价数据， N×1 double型数组，每个元素对应time中时间点的成交价。
        Volume：成交量数据，N×1 double型数组，每个元素对应time中时间点的成交量。
        Volumetick：当前tick的成交量
        Openinterest：持仓量数据，N×1 double型数组，每个元素对应time中时间点的持仓量。
        BidPrice：5个档位的买价
        BidVolume：5个档位的买量
        AskPrice：5个档位的卖价
        AskVolume：5个档位的卖量
    '''

    return init_set.traderGetTickDataV2(TargetIdx, Date, FQ)


# noinspection PyPep8Naming
# @trace_time
def traderGetCurrentBarV2():
    '''
    获得当前bar的信息 
    
    :return: barNum, barTime
    ::
    
        barNum:     double, bar索引号
        barTime: float, 当前Bar时间，以Matlab浮点数值形式存储
    ..
    
    :Example: 获取当前bar信息
    .. code-block:: python
        :linenos:
        
        from atquant import api 
        (barNumber,barTime)= api.traderGetCurrentBarV2()
    ..
    
    '''

    return init_set.traderGetCurrentBarV2()


# noinspection PyPep8Naming
# @trace_time
def traderGetTargetList():
    '''
    若在策略的调用脚本中已定义标的资产，则可在策略函数中通过此函数获取标的资产信息
    
    :return: TargetList: list, 包含标的列表的词典
    ::
    
        TargetList:列表字典类型，具体结构如下:
            Market :市场类型，字符串格式
            Code:交易品种代码，字符串格式，如'000002'
    ..
    
    :Example: 策略中获取标的资产信息
    .. code-block:: python
        :linenos:
        
        TargetList = []
        TargetList.append({'Market': 'shfe', 'Code': 'ru0000'})
        TargetList.append({'Market':'CFFEX','Code':'IF0000'})
        traderRunBacktestV2(…,TargetList, …)
        TargetList = traderGetTargetList( )
    ..
    '''

    return init_set.traderGetTargetList()


# noinspection PyPep8Naming
# @trace_time
def traderGetMainContract(Market, Code, BeginDate, EndDate):
    '''
    函数功能:获取指定市场,起始时间段,每个交易日对应的主力次主力合约
    
    :param Market:国内期货市场,如cffex,dce,zce,shfe
    :param Code:主力合约标识,如if0000,ih0000,ag0000
    :param Beginate:开始时间,如:20160101
    :param Enddate:结束时间,如:20160301
    :return: pandas.DataFrame 返回每个交易日的具体主力合约, 第一列为：'Market'， 第二列为：'Date'
    
    :Example: 获取标的信息
    .. code-block:: python
        :linenos:
        
        from atquant import api
        df = api.traderGetMainContract('cffex','if0000',20160101,20160102)
    ..
    >>> df
       Market      Date
    0  IF1601  20160101
    '''

    return init_set.traderGetMainContract(Market, Code, BeginDate, EndDate)


# noinspection PyPep8Naming
# @trace_time
def traderGetTargetInfo(Market, Code):
    '''
    获取标的基本信息

    :param Market: str,市场类型,允许值如下：
    ::
            
        'SZSE’：深圳股票
        'SSE'：上海股票
        'SHFE'：上海期货
        'DCE' ：大连商品
        'CZCE'：郑州商品
        'CFFEX'：中金所
    ..
    :param Code: str, 交易品种代码，如'IF0000'
    :return: Info:标的基本信息，词典类型
    :Example: 获取标的信息
    .. code-block:: python
        :linenos:
        
        from atquant import api
        Info= api.traderGetTargetInfo('szse','000004')
    '''

    return init_set.traderGetTargetInfo(Market, Code)


# noinspection PyPep8Naming
# @trace_time
def traderGetTargetInfoV2(TargetIdxA):
    '''
    获取标的基本信息
    
    :param TargetIdxA: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray, 输入标的的索引，从0开始计算。
    :return: pandas.DataFrame, 包含标的信息
    :Example: 获取标的信息
    .. code-block:: python
        :linenos:
        
        from atquant import api
        # 假设输入标的列表，TargetList = [{'Market': 'SHFE', 'Code': 'AL0000'},{'Market': 'SHFE', 'Code': 'RB0000'}] 
        # 获取标的0的基本信息，即AL0000的基本信息
        Info = api.traderGetTargetInfoV2(0)
    '''

    return init_set.traderGetTargetInfoV2(TargetIdxA)


# noinspection PyPep8Naming
# @trace_time
def traderGetAccountInfoV2(HandleIdx):
    '''
    通过账户句柄索引序列号获得账户当前资金情况

    :param HandleIdx: numpy.asarray函数支持的数据类型,比如: int, float, list, tuple, np.arrray, 账户句柄索引，从0开始计数
    :return: ValidCash, HandListCap，OrderFrozen, MarginFrozen，PositionProfit
    :: 
        
        ValidCash: numpy.ndarray，账户当前可用资金
        HandListCap: numpy.ndarray，账户当前总动态权益
        OrderFrozen: numpy.ndarray, 下单冻结资金总额
        MarginFrozen: numpy.ndarray, 保证金冻结资金总额
        PositionProfit: numpy.ndarray, 持仓盈亏
    ..
    :Example: 获取账户信息
    .. code-block:: python
        :linenos:
        
        from atquant import api
        # 假设输入账户列表，AccountList = ['FutureBackReplay']
        Info = api.traderGetAccountInfoV2(0)
    '''

    return init_set.traderGetAccountInfoV2(HandleIdx)


# noinspection PyPep8Naming
# @trace_time
def traderGetAccountPositionV2(HandleIdx, TargetIdx):
    '''
    获得当前仓位信息。
    
    :param HandleIdx: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray, 账户句柄索引序列号
    :param TargetIdx: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray, 交易标的索引序列号
    :return: Position, Frozen, AvgPrice
    ::
    
        Position：   numpy.ndarray，当前多头或者空头持仓
        Frozen：     numpy.ndarray，当前多头或者空头冻结持仓
        AvgPrice：   numpy.ndarray，当前多头或者空头平均价格
    ..
    :Example:
    .. code-block:: python
        :linenos:
        
        AccountList = [' StockBackReplay']
        TargetList = [{'Market': 'shfe', 'Code': 'ru0000'},{'Market': 'CFFEX', 'Code': 'IF0000'}]
        # 获得代码为'IF0000'期货在'StockBackReplay'账号中的仓位信息
        from atquant import api
        (Position, Frozen, AvgPrice) = api.traderGetAccountPositionV2(0,0)
    '''

    return init_set.traderGetAccountPositionV2(HandleIdx, TargetIdx)


# noinspection PyPep8Naming
# @trace_time
def traderGetAccountPositionDirV2(HandleIdx, TargetIdx, LongShort):
    '''
    获得当前多头或者空头的仓位信息。

    :param HandleIdx: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray, 账户句柄索引序列号,从0开始计数。回测模式只允许单账号
    :param TargetIdx: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray, 交易标的索引序列号,从0开始计数
    :param LongShort: str, 输入为'Long'表示多头，或者'Short'表示空头
    :return: Position, Frozen, AvgPrice
    ::

        Position：   numpy.ndarry，当前多头或者空头持仓
        Frozen：     numpy.ndarry，当前多头或者空头冻结持仓
        AvgPrice：   numpy.ndarry，当前多头或者空头平均价格
    ..
    :Example:
    .. code-block:: python
        :linenos:

        AccountList = ['StockBackReplay']
        TargetList = [{'Market':'CFFEX','Code':'IF0000'}]
        # 获得代码为'IF0000'期货在'StockBackReplay'账号中的空头持仓信息
        from atquant import api
        (Position, Frozen, AvgPrice) = api.traderGetAccountPositionDirV2(0, [0, 1], 'Short')
    '''

    return init_set.traderGetAccountPositionDirV2(HandleIdx, TargetIdx, LongShort)


# noinspection PyPep8Naming
# @trace_time
def traderBuyV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag):
    '''
    买入下单，若初始有空头持仓，则先平仓，再买入。

    :param HandleIdx: int or squence, 账户句柄索引序列号
    :param TargetIdx: int or sequence,交易标的索引序列号，可以为单个数字或一个序列
    :param Contracts: int or str,下单数量，当为 'all' 时将现有持仓全部平仓
    :param Price: float, 价格，此处为下单价格
    :param PriceType: str, 单价格类型，允许值如下:
        ::
            'market'：市价
            'limit'：限价
        ..
    :param OrderTag: str, 订单标记
    :return: int, 订单号
    .. note::
        
        | 若计划买开5手，
        | 无持仓，直接买开5手多单，最后持仓是:5手多单
        | 原有3手空单，则市价平3手空单，再买开5手多单，最后持仓是:5手多单
        | 原有2手多单，再买开5手多单，最后持仓是:2+5=7手多单
    ..
    .. code-block:: python
        :linenos:
        
        from atquant import api
        AccountList = ['StockBackReplay']
        TargetList = [{'Market':'CFFEX','Code':'IF0000'}]
        # 市价买入股指期货IF0000  10手（若初始有空头持仓，则先将空头持仓全部平仓,再买入10手），并将此买入操作标记为'buy'。
        orderID = api.traderBuyV2(0, 0, 10 ,0,'market','buy')
    '''

    return init_set.traderBuyV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderSellShortV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag):
    '''
    卖出下单，若初始有多头持仓，则先平仓，再卖出。

    :param HandleIdx: int, 账户句柄索引序列号
    :param TargetIdx: int, 交易标的索引序列号
    :param Contracts: int, 下单数量
    :param Price: int or float, 价格，此处为下单价格
    :param PriceType: str, 下单价格类型，允许值如下:
        ::
            'market'：市价
            'limit'：限价
        ..
    :param OrderTag: str, 订单标记
    :return: int, 订单号
    
    .. note:: 若计划卖开5手，
    
        | 账号无持仓，直接卖开5手空单，最后持仓：5手空单
        | 有3手多单,先市价平3手多单,在卖开5手空单,最后持仓:5手空单
        | 有2手空单,再卖开5手空单,最后持仓:2+5=7手空单
    ..    
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        TargetList = [{'Market':'CFFEX', 'Code': 'IF0000'}]
        AccountList = ['StockBackReplay']
        # 市价卖出'StockBackReplay'中股指期货'IF0000'主力合约100手(若初始有多头持仓，则先全部平仓，再卖出100手)，并将此操作标记为'sell'
        orderID = api.traderSellShortV2 (0, 0,100 ,0,'market','sell')
    '''

    return init_set.traderSellShortV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderBuyToCoverV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag):
    '''
    买入平仓,前提是有空仓,否则操作无效。

    :param HandleIdx: int, 账户句柄索引序列号
    :param TargetIdx: int, 交易标的索引序列号
    :param Contracts: int, 下单数量
    :param Price: int or float, 价格，此处为下单价格
    :param PriceType: str, 下单价格类型，允许值如下:
        ::
            'market'：市价
            'limit'：限价
        ..
    :param OrderTag: str, 订单标记
    :return: int or None, 订单号

    .. note:: 若计划买开5手，

        | 账号无持仓,最后无持仓
        | 有6手空单,计划买平5手后,账号最后持仓为:max(6-5,0)=1,即最后要么还有1手空单,要么无持仓
        | 有2手多单，最后持仓：2手多单    
    ..    
    '''

    return init_set.traderBuyToCoverV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderDirectBuyV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag):
    '''
    买入下单，初始持仓无影响。

    :param HandleIdx: int, 账户句柄索引序列号
    :param TargetIdx: int, 交易标的索引序列号
    :param Contracts: int, 下单买入数量
    :param Price: int or float, 价格，此处为下单价格
    :param PriceType: str, 下单价格类型，允许值如下:
        ::
            'market'：市价
            'limit'：限价
        ..
    :param OrderTag: str, 订单标记
    :return: int, 订单号
    .. note:: 若计划买开5手，

        | 无持仓，直接买开5手，最后持仓为：5手多单
        | 账号已有空单,
            | 如果空单数量大，例如空单7手，则最后仓位为:7-5=2手空单
            | 如果买开数量大，例如空单3手，则最后仓位为:5-3=2手多单
        | 账号已有3手买开，再买开5手，最后持仓是3+5=8手多单    
    ..    
    :Exmaple:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        # 以21.3元/股的价格买入1000股代码为000001的股票，并将此买入操作标记为'1'
        orderID =  api.traderDirectBuy (Handle, 'SZSE', '000001' ,1000,21.3,'limit','1')
    '''

    return init_set.traderDirectBuyV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderSellV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag):
    '''
    多单的平仓下单，即卖出平仓下单。

    :param HandleIdx: int, 账户句柄索引序列号
    :param TargetIdx: int, 交易标的索引序列号
    :param Contracts: int, 平仓数量
    :param Price: int or float, 价格，此处为下单价格
    :param PriceType: str,下单价格类型:
        ::
            'market'：市价
            'limit'：限价
        ..
    :param OrderTag: 
    :param OrderTag: str, 订单标记
    :return: int, 订单号
    
    .. note:: 若计划卖平5手，

        | 无持仓，此次卖平无效，最后无持仓
        | 原有2手空单,此次卖平无效,维持卖平前的一切状态,最后持仓是:2手空单
        | 若有7手多单，计划卖平5手后，账号最后持仓为：max(7-5,0)=2，即要么还有7-5=2手多单，要么无持仓    
    ..
    
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        TargetList = [({'Market': 'CFFEX', 'Code': 'IF0000'}]
        AccountList = ['FutureSimAcc','StockSimAcc']
        # 将StockSimAcc中股票代码为600001的股票全部平仓，并将此操作标记为’sell’。
        orderID = traderSellV2(2, 1, 'all',0,'market','1')
        # 以2685的价格平仓期货IF0000:若初始为空头持仓，不操作；若初始多头持仓小于500，卖出平仓，使当前持仓为0；若初始多头持仓大于500，则卖出平仓数量500手。
        orderID = traderSellV2(1, 2, 500, 2685, 'limit', '1')

    
    '''

    return init_set.traderSellV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderDirectSellV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag):
    '''
    卖出下单，初始持仓无影响。

    :param HandleIdx: int, 账户句柄索引序列号
    :param TargetIdx: int, 交易标的索引序列号
    :param Contracts: int, 下单数量
    :param Price: float, 价格，此处为下单价格
    :param PriceType: str,下单价格类型:
        ::
            'market'：市价
            'limit'：限价
        ..
    :param OrderTag: str, 订单标记
    :return: orderID, int, 订单编号
    '''

    return init_set.traderDirectSellV2(HandleIdx, TargetIdx, Contracts, Price, PriceType, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderCloseAllV2(HandleIdx):
    '''平指定帐号所有持仓(不包含冻结部分)'''

    return init_set.traderCloseAllV2(HandleIdx)


# noinspection PyPep8Naming
# @trace_time
def traderPositionToV2(HandleIdx, TargetIdx, Position, Price, PriceType, OrderTag):
    '''
    调仓到指定仓位。

    :param HandleIdx: int,账户句柄索引序列号.
    :param TargetIdx: int, 交易标的索引序列号.
    :param Position: int,目标仓位，如-5表示调整至5手空单。
    :param Price: float,价格，此处为下单价格,为0时表示市价。
    :param PriceType: str,下单价格类型: 
        ::
            'market'：市价
            'limit'：限价
        ..
    :param OrderTag: str, 订单标记
    :return: int or numpy.nan, 订单号
    :Example:
    .. code-block:: python
        :linenos:
        
        import atquant.api as api
        AccountList = ['FutureSimAcc']
        TargetList = [{'Market': 'CFFEX', 'Code': 'IF0000'}]
        # 将StockSimAcc中代码为IF0000的期货仓位以市价调整到5，并将此操作标记为'buy'
        api.traderPositionToV2(0, 0, 5, 0, 'market', 'buy')

    ..  
    .. note::
        
        | 计划调整为指定仓位:5，（多单或者空单）
        | 1. 账号无持仓:则相应开多或者开空5手
        | 2. 初始持仓为3手多单:
        | 计划调整为5手空单,平3手多单,开5手空单,最后持仓:5手空单
        | 计划调整为5手多单,最后持仓:5手多单
        | 3. 初始持仓为2手空单:
        | 计划调整为5手多单,则平2手空单,再开5手多单,最后持仓:5手多单
        | 计划调整为5手空单,最后持仓:5手空单
    ..
    '''

    return init_set.traderPositionToV2(HandleIdx, TargetIdx, Position, Price, PriceType, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderConfigTo(HandleIdx, TargetIdx_bool, Config):
    '''
    对账户进行配置:配置型回测专用，与traderBuy等交易函数不能混用, 若每根 bar 多次操作最后一次操作有效
    
    :param HandleIdx: int, 账户句柄索引
    :param TargetIdx_bool: numpy.asarray函数支持的输入数据,比如: int, float, list, tuple, np.arrray,内部转为numpy.ndarry,类型dtype=numpy.bool结构
    :param Config: numpy.asarray函数支持的输入数据,比如: int, float, list, tuple, np.arrray，配置数值矩阵, 跟策略脚本使用的 targetList 同维.当 -1 < config < 1 时, 数值表示配资百分比; 当 config >= 1, 或 config <= -1 时, 表示数量基本单位
    :return: None
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        TargetList = [{'Market': 'CFFEX', 'Code': 'IF0000'},
                   {'Market': 'szse', 'Code': '600001'}]
        AccountList = ['FutureSimAcc', 'StockSimAcc']
        # 将FutureSimAcc中账户权益的57 % 用于标的IF0000开空仓
        api.traderConfigTo(0, [0, 1], [0, 0.57])
        # 将StockSimAcc账户买入400股600001
        api.traderConfigTo(1, [1, 0], [400, 0])
    '''

    return init_set.traderConfigTo(HandleIdx, TargetIdx_bool, Config)


# noinspection PyPep8Naming
# @trace_time
def traderGetAccountConfig(HandleIdx, TargetIdx):
    '''
    获取当前账户的配置信息。

    :param HandleIdx: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray。内部转为numpy.ndarry,类型dtype=numpy.int结构，表示账户的句柄索引，从0开始计数
    :param TargetIdx: numpy.asarray函数支持的数据类型,比如: int, float, list,tuple, np.arrray。内部转为numpy.ndarry,类型dtype=numpy.int结构，表示交易标的索引序列号，从0开始计数 
    :return: Config,numpy.ndarray
    ::
        当-1<config<1时，数值表示配资百分比；
        当config>=1，或config<=-1时，表示数量基本单位
    ..
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        # 暂时只支持在回测模式中使用
        api.traderConfigTo(0, 0, -0.57)
        Config = api.traderGetAccountConfig(0, 0)  
    '''

    return init_set.traderGetAccountConfig(HandleIdx, TargetIdx)


# noinspection PyPep8Naming
# @trace_time
def traderGetCodeList(block, **kwargs):
    '''
    获得指数（包含权重和成分股）、行业板块（没有权重，只有成分股）、地域板块（没有权重，只有成分股）、期权板块的信息，包括成分股及权重等信息

    :param block: str,板块或指数的名称
    :param kwargs: dict, 其他可选参数可包含:
    ::
        date: int, 数字型日期，比如：20150101， 默认值为0
    ..
    
    .. note::

       | index:          取所有指数
       | plate_area:     取所有地区板块
       | plate_industry: 取行业板块
       | option:         取期权
       | sse,szse,cffex,shfe,dce,czce：取各交易所品种代码
       | cffex000,cffex001,shfe000,shfe001等：取商品期货交易所主力，次主力合约代码表
       | index/plate_area/plate_industry的BlockName:获取成分股
       | 也可以输入具体的指数或板块查看成分股信息，比如已经知道沪深300的BlockName为'HS300',只需输入:
        
        >>> results = api.traderGetCodeList('HS300')
        >>> results = api.traderGetCodeList('HS300',date=20150101)
    ..
    
    :return: list：列表词典，指数、行业板块、地域板块所对应的词典信息：
    ::
        
            Market：市场
            Code：代码
            Name：板块或指数的详细名称
            BlockName：输入的板块或指数名称
            Weight：权重
    ..
    '''

    return init_set.traderGetCodeList(block, **kwargs)


# noinspection PyPep8Naming
# @trace_time
def traderGetRegUserIndi(Idx, length, *args):
    '''
    根据已注册的用户自建因子序列获取数据索引序列
    此处每次取出的交易因子有可能为多个，因此返回的结果为二维数组

    :param Idx: numpy.ndarry, 用户注册自建因子时返回的索引序列号
    :param length: int,序列长度。例120，表示返回从当前开始往前的120个数据序列。
    :param args: 函数固定结构，并行计算中的入参模式。有函数入参时必须将该参数入参。
    :return: 自定义输出值。
    :Example:
    .. code-block:: python
        :linenos:

        from atquant import api
        Idx_myMean= api.traderRegUserIndi(myMean,cellPar)
        # 取出当前bar用户自己计算的因子
        Value= api.traderGetRegUserIndi(Idx,1)
    '''

    return init_set.traderGetRegUserIndi(Idx, length, *args)


# noinspection PyPep8Naming
# @trace_time
def traderRegUserIndi(F, *args):
    '''
    注册用户自建的外部因子。

    :param F: 因子计算的函数对象
    :param args: 函数入参
    :return: Idx：返回因子序列
    :Example:
    .. code-block:: python
        :linenos:

        from atquant import api
        def myMean(cellPar,bpPFCell):
            …
            return value
        # 定义上述自定义因子myMean
        Idx_myMean= api.traderRegUserIndi(myMean,cellPar)
    '''

    return init_set.traderRegUserIndi(F, *args)


# noinspection PyPep8Naming
# @trace_time
def traderStopLossByOrderV2(HandleIdx, TargetOrderID, StopGap, StopType, OrderCtg, OrderTag):
    '''
    针对某一订单以固定的点位或者比例止损（以tick数据进行匹配，仅在匹配成功时成交）

    :param HandleIdx: int, 账户句柄索引
    :param TargetOrderID: int, 止损指令针对的订单
    :param StopGap: float, 止损阈值，当stopType为'Point'时，其数值代表价格变动的点数，当stopType为'Percent'时，其数值代表价格变动百分比，如3表示3%
    :param StopType: str, 止损类型，允许值如下:
    ::
    
        'Point'：  按价格点数止损，在订单成交价格的基础上变动指定点数则触发止损条件
        'Percent'：按照价格变化的百分比率止损，在订单成交价格的基础上变动指定百分比则触发止损条件
    ..
    :param OrderCtg: str,下单价格类型，允许值如下:
    ::
    
        'market': 市价成交
        'limit': 限价成交
    ..
    :param OrderTag: str, 订单标记
    :return: ClientOrderID, 返回的订单号
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        
        TargetList = [
            {'Market': 'CFFEX', 'Code': 'IF1512'},
            {'Market': 'CFFEX', 'Code': 'IF1506'}
        ]
        
        # 市价卖出IF0000 5手，并当价格上涨10个点时止损买入5手平仓，将此止损操作标记为'stoploss1'
        orderID = api.traderSellShortV2(0, 2, 5, 0, 'market', 'sell')
        api.traderStopLossByOrder(Handle, orderID, 10, 'Point', 'market', 'stoploss1')
        # 市价卖出IF1512 2 手，并当价格上涨 5% 时止损买入 2 手平仓，将此止损操作标记为'stoploss2'
        orderID = api.traderSellShort (Handle, 'cffex', 'IF1512', 2, 0, 'market', 'sell')
        api.traderStopLossByOrder(Handle, orderID, 5, 'Percent', 'market', 'stoploss2')
    '''

    return init_set.traderStopLossByOrderV2(HandleIdx, TargetOrderID, StopGap, StopType, OrderCtg, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderStopProfitByOrderV2(HandleIdx, TargetOrderID, StopGap, StopType, OrderCtg, OrderTag):
    '''
    针对某一订单以固定的点位或者比例止盈（以tick数据进行匹配，仅在匹配成功时成交）
    
    :param HandleIdx: int, 账户索引
    :param TargetOrderID: int, 止盈指令针对的订单
    :param StopGap: float, 止盈阈值，当stopType为'Point'时，其数值代表价格变动的点数，当stopType为'Percent'时，其数值代表价格变动百分比，如3表示3%
    :param StopType: str, 止盈类型，允许值如下:
    ::
    
        'Point'：  按价格点数止盈，在订单成交价格的基础上变动指定点数则触发止盈条件
        'Percent'：按照价格变化的百分比率止盈，在订单成交价格的基础上变动指定百分比则触发止盈条件
    ..
    :param OrderCtg: str,下单价格类型，允许值如下:
    ::
    
        'market': 市价成交
        'limit': 限价成交
    ..
    :param OrderTag: str, 订单标记
    :return: ClientOrderID, 返回的订单号
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        
        TargetList = [
            {'Market': 'CFFEX', 'Code': 'IF1512'},
            {'Market': 'CFFEX', 'Code': 'IF1506'}
        ]
        
        # 市价卖出IF1506  5手，并当价格下跌20个点时买入5手平仓止盈，将此止盈操作标记为'stopprofit1'
        orderID = api.traderSellShortV2(0,1,5,0,'market','sell')
        api.traderStopProfitByOrderV2(0, orderID, 20, 'Point', 'market','stopprofit1')
        # 市价卖出IF1512  4手，并当价格下跌15% 时买入4手止盈，将此止盈操作标记为'stopprofit2'
        orderID = api.traderSellShortV2(0, 0, 4, 0, 'market', 'sell')
        api.traderStopProfitByOrderV2(0, orderID, 15, 'Percent','market','stoploss2')
    '''

    return init_set.traderStopProfitByOrderV2(HandleIdx, TargetOrderID, StopGap, StopType, OrderCtg, OrderTag)


# noinspection PyPep8Naming
# @trace_time
def traderStopTrailingByOrderV2(HandleIdx, TargetOrderID, StopGap, StopType, TrailingGap, TrailingType, OrderCtg, OrderTag):
    '''
    针对某一订单跟踪止盈（以tick数据进行匹配，仅在匹配成功时成交）
    
    :param HandleIdx: int, 账户索引
    :param TargetOrderID: int, 止盈指令针对的订单
    :param StopGap: float, 跟踪止盈触发值，当stopType为'Point'时，其数值代表价格变动的点数，当stopType为'Percent'时，其数值代表价格变动百分比，如3表示3%
    :param StopType: str, 止盈类型，允许值如下:
    ::
    
        'Point'：  按价格点数止盈，在订单成交价格的基础上变动指定点数则触发止盈条件
        'Percent'：按照价格变化的百分比率止盈，在订单成交价格的基础上变动指定百分比则触发止盈条件
    ..
    :param TrailingGap: 跟踪止盈触发的回撤条件，当trainingType为'Point'时，其数值代表价格变动的点数，当stopType为'Percent'时，其数值代表价格变动百分比，如3表示3%。若价格先触及stopGap,又触及此条件，则进行对应的止盈下单
    :param TrailingType: 跟踪止盈类型，字符串格式，允许值如下：
    ::
    
        'Point'：  按价格点数止盈，从触发止盈条件时刻开始，回撤达到指定点数则进行止盈操作
        'Percent'：按照价格变化的百分比率止盈，从触发止盈条件时刻开始，回撤达到指定百分比则进行止盈操作
    ..
    :param OrderCtg: str,下单价格类型，允许值如下:
    ::
    
        'market': 市价成交
        'limit': 限价成交
    ..
    :param OrderTag: str, 订单标记
    :return: ClientOrderID, 返回的订单号
    :Example:
    .. code-block:: python
        :linenos:
        
        from atquant import api
        
        TargetList = [
            {'Market': 'CFFEX', 'Code': 'IF1512'},
            {'Market': 'CFFEX', 'Code': 'IF1506'}
        ]
        
        # 市价卖出IF1506  3手，并当价格上涨15个点时买入3手止损，当价格下跌25个点后回撤10个点时买入3手止盈
        orderID = api.traderSellShortV2(0, 1, 3, 0, 'market', 'sell')
        api.traderStopLossByOrderV2(0, orderID, 15, 'Point', 3, 'market', 'stoplossB') 
        # 市价卖出IF1506  3手，并当价格亏损1%时买入3手止损，当价格上涨2%后回撤所赚取点数的20%时买入3手止损
        orderID = api.traderSellShortV2(0, 1, 3, 0, 'market', 'sell'); 
        api.traderStopTrailingByOrderV2(0, orderID, 2, 'Point', 20, 'Point', 5, 'market', 'trailingB')
    '''

    return init_set.traderStopTrailingByOrderV2(HandleIdx, TargetOrderID, StopGap, StopType, TrailingGap, TrailingType, OrderCtg, OrderTag)
