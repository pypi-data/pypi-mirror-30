#!../futurav/bin/python
import traceback
import json
import imp
import urllib
import urllib2
import webbrowser
import re
import datetime
import time
import inspect
import os
import os.path
import sys
import ssl
from copy import deepcopy
import pandas as pd
import numpy as np

def loadData(marketList=None, dataToLoad=None, refresh=False, beginInSample=None, endInSample=None, dataDir = 'tickerData'):
    ''' prepares and returns market data for specified markets.

        prepares and returns related to the entries in the dataToLoad list. When refresh is true, data is updated from the Futura.ai server. If inSample is left as none, all available data dates will be returned.

        Args:
            marketList (list): list of market data to be supplied
            dataToLoad (list): list of financial data types to load
            refresh (bool): boolean value determining whether or not to update the local data from the Futura.ai server.
            beginInSample (str): a str in the format of YYYYMMDD defining the begining of the time series
            endInSample (str): a str in the format of YYYYMMDD defining the end of the time series

        Returns:
            dataDict (dict): mapping all data types requested by dataToLoad. The data is returned as a numpy array or list and is ordered by marketList along columns and date along the row.

    Copyright Futura.ai LLC - March 2015
    '''
    if marketList is None:
        print "warning: no markets supplied"
        return

    dataToLoad = set(dataToLoad)
    requiredData = set(['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'P', 'RINFO', 'p'])
    fieldNames = set()

    dataToLoad.update(requiredData)

    nMarkets = len(marketList)

    # set up data director
    if not os.path.isdir(dataDir):
        os.mkdir(dataDir)

    for j in range(nMarkets):
        path = os.path.join(dataDir, marketList[j]+'.txt')

        # check to see if market data is present. If not (or refresh is true), download data from Futura.ai.
        if not os.path.isfile(path) or refresh:
            try:
                if False: #sys.version_info > (2,7,9):
                    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                    data = urllib.urlopen('http://test.futura.ai/data/' +
                                          marketList[j]+'.txt',
                                          context=gcontext).read()
                else:
                    data = urllib.urlopen('http://test.futura.ai//data/' +
                                          marketList[j]+'.txt').read()
                with open(path, 'w') as dataFile:
                    dataFile.write(data)
                print 'Downloading ' + marketList[j]

            except:
                print 'Unable to download ' + marketList[j]
                marketList.remove(marketList[j])
            finally:
                dataFile.close()

    print 'Loading Data...'
    sys.stdout.flush()
    dataDict = {}
    largeDateRange = range(datetime.datetime(1990, 1, 1).toordinal(),
                           datetime.datetime.today().toordinal() + 1)
    DATE_Large = [int(datetime.datetime.fromordinal(j).strftime('%Y%m%d')) for j in largeDateRange]


    # Loading all markets into memory.
    for i, market in enumerate(marketList):
        marketFile = os.path.join('tickerData', market+'.txt')
        data = pd.read_csv(marketFile, engine='c')
        data.columns = map(str.strip, data.columns)
        fieldNames.update(list(data.columns.values))
        data.set_index('DATE', inplace=True)
        data['DATE'] = data.index

        for j, dataType in enumerate(dataToLoad):
            if dataType == 'p':
                data.rename(columns={'p':'P'},inplace = True)
                dataType = 'P'

            if dataType != 'DATE' and dataType not in dataDict and dataType in data:
                dataDict[dataType] = pd.DataFrame(index=DATE_Large, columns=marketList)
                dataDict[dataType][market] = data[dataType]

            elif dataType != 'DATE' and dataType in data:
                dataDict[dataType][market] = data[dataType]


    # get args that are not in requiredData and fieldsNames
    additionDataToLoad = dataToLoad.difference(requiredData.union(fieldNames))
    additionDataFailed = set([])
    for i, additionData in enumerate(additionDataToLoad):
        filePath = os.path.join('tickerData', additionData + '.txt')
        # check to see if data is present. If not (or refresh is true), download data from Futura.ai.
        if not os.path.isfile(filePath) or refresh:
            try:
                if False: #sys.version_info > (2,7,9):
                    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                    data = urllib.urlopen('http://test.futura.ai/data/' +
                                          additionData+'.txt',
                                          context=gcontext).read()
                else:
                    data = urllib.urlopen('http://test.futura.ai/data/' +
                                          additionData+'.txt').read()
                with open(filePath, 'w') as dataFile:
                    dataFile.write(data)
                print 'Downloading ' + additionData
            except:
                print 'Unable to download ' + additionData
                additionDataFailed.add(additionData)
                continue
            finally:
                dataFile.close()

        # read data from text file and load to memory
        data = pd.read_csv(filePath, engine='c')
        data.columns = map(str.strip, data.columns)
        data.set_index('DATE', inplace=True)
        data['DATE'] = data.index
        for j, column in enumerate(data.columns):
            if column != 'DATE':
                if additionData not in dataDict:
                    columns = set(data.columns)
                    columns.remove('DATE')
                    dataDict[additionData] = pd.DataFrame(index=DATE_Large, columns=columns)
                dataDict[additionData][column] = data[column]

    additionDataToLoad = additionDataToLoad.difference(additionDataFailed)
    # fill the gap for additional data for the whole data range
    for i, additionData in enumerate(additionDataToLoad):
        dataDict[additionData][:] = fillnans(dataDict[additionData].values)

    # drop rows in CLOSE if none of the markets have data on that date
    dataDict['CLOSE'].dropna(how='all', inplace=True)

    # In-sample date management.
    if beginInSample is not None:
        beginInSample = datetime.datetime.strptime(beginInSample, '%Y%m%d')
    else:
        beginInSample = datetime.datetime(1990, 1, 1)
    beginInSampleInt = int(beginInSample.strftime('%Y%m%d'))

    if endInSample is not None:
        endInSample = datetime.datetime.strptime(endInSample, '%Y%m%d')
        endInSampleInt = int(endInSample.strftime('%Y%m%d'))
        dataDict['DATE'] = dataDict['CLOSE'].loc[beginInSampleInt:endInSampleInt, :].index.values
    else:
        dataDict['DATE'] = dataDict['CLOSE'].loc[beginInSampleInt:, :].index.values

    for index, dataType in enumerate(dataToLoad):
        if dataType != 'DATE' and dataType in dataDict:
            dataDict[dataType] = dataDict[dataType].loc[dataDict['DATE'], :]
            dataDict[dataType] = dataDict[dataType].values

    if 'VOL' in dataDict:
        dataDict['VOL'][np.isnan(dataDict['VOL'].astype(float))] = 0.0
    if 'OI' in dataDict:
        dataDict['OI'][np.isnan(dataDict['OI'].astype(float))] = 0.0
    if 'R' in dataDict:
        dataDict['R'][np.isnan(dataDict['R'].astype(float))]=0.0
    if 'RINFO' in dataDict:
        dataDict['RINFO'][np.isnan(dataDict['RINFO'].astype(float))]=0.0
        dataDict['RINFO'] = dataDict['RINFO'].astype(float)
    if 'P' in dataDict:
        dataDict['P'][np.isnan(dataDict['P'].astype(float))]=0.0

    dataDict['CLOSE'] = fillnans(dataDict['CLOSE'])

    dataDict['OPEN'], dataDict['HIGH'], dataDict['LOW'] = fillwith(dataDict['OPEN'],dataDict['CLOSE']), fillwith(dataDict['HIGH'],dataDict['CLOSE']), fillwith(dataDict['LOW'],dataDict['CLOSE'])

    print '\bDone! \n',
    sys.stdout.flush()

    return dataDict


def runts(tradingSystem, plotEquity=True, reloadData=False, state={}, sourceData='tickerData'):
    ''' backtests a trading system.

    evaluates the trading system function specified in the argument tsName and returns the struct ret. runts calls the trading system for each period with sufficient market data, and collets the returns of each call to compose a backtest.

    Example:

    # Might want to change this comment
    s = runts('tsName') evaluates the trading system specified in string tsName, and stores the result in struct s.

    Args:

        tsName (str): Specifies the trading system to be backtested
        plotEquity (bool, optional): Show the equity curve plot after the evaluation
        reloadData (bool,optional): Force reload of market data.
        state (dict, optional):  State information to resume computation of an existing backtest (for live evaluation on Futura.ai servers). State needs to be of the same form as ret.

    Returns:
        a dict mapping keys to the relevant backesting information: trading system name, system equity, trading dates, market exposure, market equity, the errorlog, the run time, the system's statistics, and the evaluation date.

        keys and description:
            'tsName' (str):    Name of the trading system, same as tsName
            'fundDate' (int):  All dates of the backtest in the format YYYYMMDD
            'fundEquity' (float):    Equity curve for the fund (collection of all markets)
            'returns' (float): Marketwise returns of trading system
            'marketEquity' (float):    Equity curves for each market in the fund
            'marketExposure' (float):    Collection of the returns p of the trading system function. Equivalent to the percent expsoure of each market in the fund. Normalized between -1 and 1
            'settings' (dict):    The settings of the trading system as defined in file tsName
            'errorLog' (list): list of strings with error messages
            'runtime' (float):    Runtime of the evaluation in seconds
            'stats' (dict): Performance numbers of the backtest
            'evalDate' (datetime): Last market data present in the backtest

    Copyright Futura.ai LLC - March 2015
    '''

    errorlog=[]
    ret={}

    if type(tradingSystem) is str:
        tradingSystem = tradingSystem.replace('\\', '/')

    filePathFlag = False
    if str(type(tradingSystem)) == "<type 'classobj'>" or str(type(tradingSystem)) == "<type 'type'>":
        TSobject = tradingSystem()
        settings = TSobject.mySettings()
        tsName = str(tradingSystem)

    elif str(type(tradingSystem)) == "<type 'instance'>" or str(type(tradingSystem)) == "<type 'module'>":
        TSobject = tradingSystem
        settings = TSobject.mySettings()
        tsName = str(tradingSystem)

    elif os.path.isfile(tradingSystem):
        filePathFlag = True
        filePath = str(tradingSystem)
        tsFolder, tsName = os.path.split(filePath)
        print filePath
        try:
            TSobject = imp.load_source('tradingSystemModule', filePath)
        except Exception as e:
            print 'Error loading trading system'
            print str(e)
            print traceback.format_exc()
            return

        try:
            settings = TSobject.mySettings()
        except Exception as e:
            print "Unable to load settings. Please ensure your settings definition is correct"
            print str(e)
            print traceback.format_exc()
            return

    else:
        print "Please input your trading system's file path or a callable object."
        return

    if isinstance(state, dict):
        if 'save' not in state:
            state['save']=False
        if 'resume' not in state:
            state['resume']=False
        if 'runtimeInterrupt' not in state:
            state['runtimeInterrupt'] = False
    else:
        print 'state variable is not a dict'

    # get boolean index of futures
    futuresIx = np.array(map(lambda string:bool(re.match("F_",string)),settings['markets']))

    # get data fields and extract them.
    requiredData = set(['DATE','OPEN','HIGH', 'LOW', 'CLOSE', 'P','RINFO','p'])
    dataToLoad = requiredData

    tsArgs = inspect.getargspec(TSobject.myTradingSystem)
    tsArgs = tsArgs[0]
    tsDataToLoad = [item for index, item in enumerate(tsArgs) if item.isupper()]

    dataToLoad.update(tsDataToLoad)

    global settingsCache
    global dataCache

    if 'settingsCache' not in globals() or settingsCache != settings:
        if 'beginInSample' in settings and 'endInSample' in settings:
            dataDict=loadData(settings['markets'],dataToLoad,reloadData, beginInSample = settings['beginInSample'], endInSample = settings['endInSample'], dataDir=sourceData)
        elif 'beginInSample' in settings and 'endInSample' not in settings:
            dataDict=loadData(settings['markets'],dataToLoad,reloadData, settings['beginInSample'], dataDir=sourceData)
        elif 'endInSample' in settings and 'beginInSample' not in settings:
            dataDict=loadData(settings['markets'],dataToLoad,reloadData, endInSample = settings['endInSample'], dataDir=sourceData)
        else:
            dataDict=loadData(settings['markets'],dataToLoad,reloadData, dataDir=sourceData)

        dataCache=deepcopy(dataDict)
        settingsCache = deepcopy(settings)

    else:
        print 'copying data from cache'
        settings= deepcopy(settingsCache)
        dataDict = deepcopy(dataCache)

    print 'Evaluating Trading System'

    nMarkets=len(settings['markets'])
    endLoop=len(dataDict['DATE'])


    #print endLoop
    #exit()

    if 'RINFO' in dataDict:
        Rix= dataDict['RINFO'] != 0
    else:
        dataDict['RINFO'] = np.zeros(np.shape(dataDict['CLOSE']))
        Rix = np.zeros(np.shape(dataDict['CLOSE']))

    dataDict['exposure']=np.zeros((endLoop,nMarkets))
    dataDict['equity']=np.ones((endLoop,nMarkets))
    dataDict['fundEquity'] = np.ones((endLoop,1))
    realizedP = np.zeros((endLoop, nMarkets))
    returns = np.zeros((endLoop, nMarkets))

    sessionReturnTemp = np.append( np.empty((1,nMarkets))*np.nan,(( dataDict['CLOSE'][1:,:]- dataDict['OPEN'][1:,:]) / dataDict['CLOSE'][0:-1,:] ), axis =0 ).copy()
    sessionReturn=np.nan_to_num( fillnans(sessionReturnTemp) )
    #print sessionReturn
    #exit()
    gapsTemp=np.append(np.empty((1,nMarkets))*np.nan, (dataDict['OPEN'][1:,:]- dataDict['CLOSE'][:-1,:]-dataDict['RINFO'][1:,:].astype(float)) / dataDict['CLOSE'][:-1:],axis=0)
    gaps=np.nan_to_num(fillnans(gapsTemp))

    # check if a default slippage is specified
    if False == settings.has_key('slippage'):
        settings['slippage'] = 0.05

    slippageTemp = np.append(np.empty((1,nMarkets))*np.nan, ((dataDict['HIGH'][1:,:] - dataDict['LOW'][1:,:]) / dataDict['CLOSE'][:-1,:] ), axis=0) * settings['slippage']
    SLIPPAGE = np.nan_to_num(fillnans(slippageTemp))
    #print 'SLIPPAGE=',SLIPPAGE
    if 'lookback' not in settings:
        startLoop=2
        settings['lookback']=1
    else:
        startLoop= settings['lookback']-1


    # Server evaluation --- resumes for new day.
    if state['resume']:
        if 'evalData' in state:
            ixOld= dataDict['DATE']<=state['evalData']['evalDate']
            evalData=state['evalData']

            ixMapExposure=np.concatenate(([False,False],ixOld),axis=0)
            dataDict['equity'][ixOld,:]=state['evalData']['marketEquity']
            dataDict['exposure'][ixMapExposure,:]=state['evalData']['marketExposure']
            dataDict['fundEquity'][ixOld,:] = state['evalData']['fundEquity']

            startLoop = np.shape(state['evalData']['fundDate'])[0]
            endLoop = np.shape(dataDict['DATE'])[0]

            print('Resuming'+tsName+' | computing '+str(endLoop-startLoop+1)+' new days')
            settings= evalData['settings']

    t0= time.time()

    print startLoop,endLoop

    # Loop through trading days
    for t in range(startLoop,endLoop):
        todaysP= dataDict['exposure'][t-1,:]

        yesterdaysP = realizedP[t-2,:]
        deltaP=todaysP-yesterdaysP

        print '-----',dataDict['DATE'][t],'---------'
        print '[todaysP=', todaysP,']'
        print '[yesterdaysP=', yesterdaysP,']'
        print '[sessionReturn=', sessionReturn[t,:],']'
        print '[gaps=', gaps[t,:],']'

        newGap=yesterdaysP * gaps[t,:]
        newGap[np.isnan(newGap)]= 0

        newRet = todaysP * sessionReturn[t,:] - abs(deltaP * SLIPPAGE[t,:])
        newRet[np.isnan(newRet)] = 0
        print '[newRet=', newRet,']'
        print '[newGap=', newGap,']'
        print '[deltaP=', deltaP,']'
        print '[deltaP * SLIPPAGE[t,:]=', abs(deltaP * SLIPPAGE[t,:]),']'

        returns[t,:] = newRet + newGap
        print '[returns=', returns[t,:],']'
        dataDict['equity'][t,:] = dataDict['equity'][t-1,:] * (1+returns[t,:])
        dataDict['fundEquity'][t] = (dataDict['fundEquity'][t-1] * (1+np.sum(returns[t,:])))
        print '[equity=', dataDict['equity'][t,:],']'
        realizedP[t-1,:] = dataDict['CLOSE'][t,:] / dataDict['CLOSE'][t-1,:] * dataDict['fundEquity'][t-1] / dataDict['fundEquity'][t] * todaysP

        #print '[CLOSED=',dataDict['CLOSE'][t],'][CLOSED DIFF=', dataDict['CLOSE'][t,:]-dataDict['CLOSE'][t-1,:],

        print '[fundEquity=', dataDict['fundEquity'][t],']'
        print '[RealizedP=', realizedP[t-1],']'

        #exit()
        # Roll futures contracts.
        if np.any(Rix[t,:]):
            delta=np.tile(dataDict['RINFO'][t,Rix[t,:]],(t,1))
            dataDict['CLOSE'][0:t,Rix[t,:]] = dataDict['CLOSE'][0:t,Rix[t,:]].copy() + delta.copy()
            dataDict['OPEN'][0:t,Rix[t,:]] = dataDict['OPEN'][0:t,Rix[t,:]].copy()  + delta.copy()
            dataDict['HIGH'][0:t,Rix[t,:]] = dataDict['HIGH'][0:t,Rix[t,:]].copy() + delta.copy()
            dataDict['LOW'][0:t,Rix[t,:]] = dataDict['LOW'][0:t,Rix[t,:]].copy()   + delta.copy()

        try:
            argList= []

            for index in range(len(tsArgs)):
                if tsArgs[index]=='settings':
                    argList.append(settings)
                elif tsArgs[index] == 'self':
                    continue
                else:
                    argList.append(dataDict[tsArgs[index]][t- settings['lookback'] +1:t+1].copy())
            #print argList
            #exit()
            position, settings= TSobject.myTradingSystem(*argList)
        except:
            print 'Error evaluating trading system'
            print sys.exc_info()[0]
            print traceback.format_exc()
            errorlog.append(str(dataDict['DATE'][t])+ ': ' + str(sys.exc_info()[0]))
            dataDict['equity'][t:,:] = np.tile(dataDict['equity'][t,:],(endLoop-t,1))
            return
        position[np.isnan(position)] = 0
        position = np.real(position)
        position = position/np.sum(abs(position))
        position[np.isnan(position)] = 0  # extra nan check in case the positions sum to zero


        dataDict['exposure'][t,:] = position.copy()

        t1=time.time()
        runtime = t1-t0
        if runtime > 300 and state['runtimeInterrupt']:
            errorlog.append('Evaluation stopped: Runtime exceeds 5 minutes.')
            break

    if 'budget' in settings:
        fundequity = dataDict['fundEquity'][(settings['lookback']-1):,:] * settings['budget']
    else:
        fundequity = dataDict['fundEquity'][(settings['lookback']-1):,:]
    #print '---fundequity---:',fundequity
    #print '---dataDict[exposure]---:',dataDict

    marketRets = np.float64(dataDict['CLOSE'][1:,:] - dataDict['CLOSE'][:-1,:] - dataDict['RINFO'][1:,:])/dataDict['CLOSE'][:-1,:]
    marketRets = fillnans(marketRets)
    marketRets[np.isnan(marketRets)] = 0
    marketRets = marketRets.tolist()
    a = np.zeros((1,nMarkets))
    a = a.tolist()
    marketRets = a + marketRets

    ret['returns'] = np.nan_to_num(returns).tolist()

    if errorlog:
        print 'Error: {}'.format(errorlog)

    if plotEquity:
        statistics = stats(fundequity)
        print statistics
        from guiBackends.tkbackend import plotts
        returns = plotts(tradingSystem, fundequity,dataDict['equity'], dataDict['exposure'], settings, dataDict['DATE'][settings['lookback']-1:], statistics,ret['returns'],marketRets)

    else:
        statistics= stats(fundequity)


    ret['tsName']=tsName
    ret['fundDate']=dataDict['DATE'].tolist()
    ret['fundEquity']=dataDict['fundEquity'].tolist()
    ret['marketEquity']= dataDict['equity'].tolist()
    ret['marketExposure'] = dataDict['exposure'].tolist()
    ret['errorLog']=errorlog
    ret['runtime']=runtime
    ret['stats']=statistics
    ret['settings']=settings
    ret['evalDate']=dataDict['DATE'][t]
    #print ret
    if state['save']:
        with open(tsName+'.json', 'w+') as fileID:
            stateSave=json.dump(ret,fileID)
    return ret


def stats(equityCurve):
    ''' calculates trading system statistics

    Calculates and returns a dict containing the following statistics
    - sharpe ratio
    - sortino ratio
    - annualized returns
    - annualized volatility
    - maximum drawdown
        - the dates at which the drawdown begins and ends
    - the MAR ratio
    - the maximum time below the peak value
        - the dates at which the max time off peak begin and end

    Args:
        equityCurve (list): the equity curve of the evaluated trading system

    Returns:
        statistics (dict): a dict mapping keys to corresponding trading system statistics (sharpe ratio, sortino ration, max drawdown...)

    Copyright Futura.ai LLC - March 2015

    '''
    returns = (equityCurve[1:]-equityCurve[:-1])/equityCurve[:-1]

    volaDaily=np.std(returns)
    volaYearly=np.sqrt(252)*volaDaily

    index=np.cumprod(1+returns)
    indexEnd=index[-1]

    returnDaily = np.exp(np.log(indexEnd)/returns.shape[0])-1
    returnYearly = (1+returnDaily)**252-1
    sharpeRatio = returnYearly / volaYearly

    downsideReturns = returns.copy()
    downsideReturns[downsideReturns > 0]= 0
    downsideVola = np.std(downsideReturns)
    downsideVolaYearly = downsideVola *np.sqrt(252)

    sortino = returnYearly / downsideVolaYearly

    highCurve = equityCurve.copy()

    testarray = np.ones((1,len(highCurve)))
    test = np.array_equal(highCurve,testarray[0])

    if test:
        mX = np.NaN
        mIx = np.NaN
        maxDD = np.NaN
        mar = np.NaN
        maxTimeOffPeak = np.NaN
        mtopStart = np.NaN
        mtopEnd = np.NaN
    else:
        for k in range(len(highCurve)-1):
            if highCurve[k+1] < highCurve[k]:
                highCurve[k+1] = highCurve[k]

        underwater = equityCurve / highCurve
        mi = np.min(underwater)
        mIx = np.argmin(underwater)
        maxDD = 1 - mi
        mX= np.where(highCurve[0:mIx-1] == np.max(highCurve[0:mIx-1]))
        #        highList = highCurve.copy()
        #        highList.tolist()
        #        mX= highList[0:mIx].index(np.max(highList[0:mIx]))
        mX=mX[0][0]
        mar   = returnYearly / maxDD

        mToP = equityCurve < highCurve
        mToP = np.insert(mToP, [0,len(mToP)],False)
        mToPdiff=np.diff(mToP.astype('int'))
        ixStart   = np.where(mToPdiff==1)[0]
        ixEnd     = np.where(mToPdiff==-1)[0]

        offPeak         = ixEnd - ixStart
        if len(offPeak) > 0:
            maxTimeOffPeak  = np.max(offPeak)
            topIx           = np.argmax(offPeak)
        else:
            maxTimeOffPeak = 0
            topIx          = np.zeros(0)

        if np.not_equal(np.size(topIx),0):
            mtopStart= ixStart[topIx]-2
            mtopEnd= ixEnd[topIx]-1

        else:
            mtopStart = np.NaN
            mtopEnd = np.NaN
            maxTimeOffPeak = np.NaN

    statistics={}
    statistics['sharpe']              = sharpeRatio
    statistics['sortino']             = sortino
    statistics['returnYearly']        = returnYearly
    statistics['volaYearly']          = volaYearly
    statistics['maxDD']               = maxDD
    statistics['maxDDBegin']          = mX
    statistics['maxDDEnd']            = mIx
    statistics['mar']                 = mar
    statistics['maxTimeOffPeak']      = maxTimeOffPeak
    statistics['maxTimeOffPeakBegin'] = mtopStart
    statistics['maxTimeOffPeakEnd']   = mtopEnd

    return statistics



#    return True
def computeFees(equityCurve, managementFee,performanceFee):
    ''' computes equity curve after fees

    Args:
        equityCurve (list, numpy array) : a column vector of daily fund values
        managementFee (float) : the management fee charged to the investor (a portion of the AUM charged yearly)
        performanceFee (float) : the performance fee charged to the investor (the portion of the difference between a new high and the most recent high, charged daily)

    Returns:
        returns an equity curve with the fees subtracted.  (does not include the effect of fees on equity lot size)

    '''
    returns = (np.array(equityCurve[1:])-np.array(equityCurve[:-1]))/np.array(equityCurve[:-1])
    ret = np.append(0,returns)

    tradeDays = ret > 0
    firstTradeDayRow = np.where(tradeDays is True)
    firstTradeDay = firstTradeDayRow[0][0]

    manFeeIx = np.zeros(np.shape(ret),dtype=bool)
    manFeeIx[firstTradeDay:] = 1
    ret[manFeeIx] = ret[manFeeIx] - managementFee/252

    ret = 1 + ret
    r = np.ndarray((0,0))
    high = 1
    last = 1
    pFee = np.zeros(np.shape(ret))
    mFee = np.zeros(np.shape(ret))

    for k in range(len(ret)):
        mFee[k] = last * managementFee/252 * equityCurve[0][0]
        if last * ret[k] > high:
            iFix = high / last
            iPerf = ret[k] / iFix
            pFee[k] = (iPerf - 1) * performanceFee * iFix * equityCurve[0][0]
            iPerf = 1 + (iPerf - 1) * (1-performanceFee)
            r=np.append(r,iPerf * iFix)
        else:
            r=np.append(r,ret[k])
        if np.size(r)>0:
            last = r[-1] * last
        if last > high:
            high = last

    out = np.cumprod(r)
    out = out * equityCurve[0]

    return out


def fillnans(inArr):
    ''' fills in (column-wise)value gaps with the most recent non-nan value.

    fills in value gaps with the most recent non-nan value.
    Leading nan's remain in place. The gaps are filled in only after the first non-nan entry.

    Args:
        inArr (list, numpy array)
    Returns:
        returns an array of the same size as inArr with the nan-values replaced by the most recent non-nan entry.

    '''
    inArr = inArr.astype(float)
    nanPos = np.where(np.isnan(inArr))
    nanRow = nanPos[0]
    nanCol = nanPos[1]
    myArr = inArr.copy()
    for i in range(len(nanRow)):
        if nanRow[i] > 0:
            myArr[nanRow[i], nanCol[i]] = myArr[nanRow[i]-1, nanCol[i]]
    return myArr


def fillwith(field, lookup):
    ''' replaces nan entries of field, with values of lookup.

    Args:
        field (list, numpy array) : array whose nan-values are to be replaced
        lookup (list, numpy array) : array to copy values for placement in field

    Returns:
        returns array with nan-values replaced by entries in lookup.
    '''

    out = field.astype(float)
    nanPos= np.where(np.isnan(out))
    nanRow=nanPos[0]
    nanCol=nanPos[1]

    for i in range(len(nanRow)):
        out[nanRow[i],nanCol[i]] = lookup[nanRow[i]-1,nanCol[i]]

    return out


def ismember(a, b):
    bIndex = {}
    for item, elt in enumerate(b):
        if elt not in bIndex:
            bIndex[elt] = item
    return [bIndex.get(item, None) for item in a]


