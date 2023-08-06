# -*- coding: utf-8 -*- 
import numpy as np
import taft
import shelve
from network import Network
from calcdata import CalcData
import utils

# Переменная для записи сообщений о ошибках
logMessage = ""

def getLastError():
    global logMessage
    return logMessage
# end of def getLastError()


# Загружает веса сети из файла fileName.
# Возвращает объект Network в случае успеха и None в случае ошибки.  
def loadNetwork( fileName ):
    ok = True 

    try:
        s = shelve.open( fileName, flag='r' )
    except Exception:
        ok = False

    if ok:
        try:
            weights = s['weights']
            bs = s['bs']
            activationFuncs = s['activationFuncs']
        except Exception:
            ok = True
        finally:
            s.close()

    if ok:
        numLayers = len( weights ) - 1
        numFeatures = np.shape(weights[0])[0]
        numNodes = [] 
        for i in range( numLayers ):
            numNodes.append( np.shape( weights[i] )[1] )
        numLabels = np.shape( weights[numLayers] )[1]
        network = Network( numLayers, numNodes, numFeatures, numLabels, activationFuncs=activationFuncs, weights=weights, bs=bs )
        return network

    return None
# end of loadNetwork()


# Готовит данные для обучения и тестирования сети. 
def prepareData( fileWithRates=None, rates=None, normalize=True, detachTest=20, calcData=None, precalcData=None, oneHot=True ):
    global logMessage
    logMessage = ""
    retErr = None, None

    if fileWithRates is not None:
        rates = taft.readFinam( fileWithRates ) # Читаем котировки из файла finam
        if rates is None:
            logMessage += "Failed to read rates from finam file %s.\n" % (fileWithRates)

    if rates is None:
        logMessage += "No rates.\n"
        return retErr

    op = rates['op']
    hi = rates['hi']
    lo = rates['lo']
    cl = rates['cl']
    vol = rates['vol']
    dtm = rates['dtm']
    length = rates['length']

    # If data precalculation is required
    if precalcData is not None:
        precalcData(rates)
    elif isinstance( calcData, CalcData ):
        if callable( calcData.precalcData ):
            calcData.precalcData( calcData, rates )

    if calcData is None: # If None using the built in function
        calcDataFunc = __calcData
    elif isinstance( calcData, CalcData ): # If calcData is an object
        calcDataFunc = calcData.run
    elif callable( calcData ): # If calcData is a function
        calcDataFunc = calcData
    else:
        return retErr

    nnInputs = []
    nnObserved = []
    nnProfit = []
    for i in range(length-1,0,-1):
        # Inputs
        pastRates = { 'op': op[i:], 'hi':hi[i:], 'lo':lo[i:], 'cl':cl[i:], 'vol':vol[i:], 'dtm':dtm[i:] }
        futureRates = { 'op': op[i-1::-1], 'hi':hi[i-1::-1], 'lo':lo[i-1::-1], 'cl':cl[i-1::-1], 'vol':vol[i-1::-1], 'dtm':dtm[i-1::-1] }

        res = calcDataFunc( pastRates, futureRates )
        if isinstance( res, tuple ): # Если функция вернула tuple (как результат корректного завершени работы)
            inputs, observed, profit = res 
            if inputs is None or observed is None: # Удостоверимся, что главные переменные - не None
                continue
        else: # Функция вернула не tuple - по соглашению это может быть только None, то есть "неудача"
            continue
        nnInputs.append( inputs )
        nnObserved.append( observed )
        nnProfit.append( profit )

    if len(nnInputs) == 0:
        return retErr
    if len(nnObserved) == 0:
        return retErr

    if isinstance( nnObserved[0], float ) and isinstance( calcData, CalcData ): # Instead of labels single observed float values has been received. Labeling is required. 
        if calcData.lookAheadScale is None: 
            calcData.lookAheadScale = utils.createScale( nnObserved, calcData.numLabels )
        nnLabels = []
        for observedIndex in range( len(nnObserved) ):
            label = calcData.getLabelByScale( nnObserved[observedIndex] )
            if oneHot:
                labels = np.zeros( shape=[calcData.numLabels], dtype=np.float32 )
                labels[label] = 1
                nnLabels.append( labels )
            else:
                nnLabels.append(label)
    else:
        nnLabels = nnObserved

    nnInputs = np.array( nnInputs, dtype='float' )
    numSamples, numFeatures = np.shape( nnInputs )
    nnLabels = np.array( nnLabels, dtype='float' )
    if oneHot:
        numLabels = np.shape( nnLabels )[1]
    else:
        numLabels = int( np.max( nnLabels ) + 1 )       
    nnProfit = np.array( nnProfit, dtype='float' )      
    nnMean = np.zeros( shape=[numFeatures], dtype='float' )
    nnStd = np.zeros( shape=[numFeatures], dtype='float' )

    if detachTest is not None:
        detachStart = int( float(numSamples) * detachTest / 100.0 )

    if normalize: # Если нужна нормализация
        normIntervalStart = 0
        if detachTest is not None:
            normIntervalStart = detachStart

        for i in range(numFeatures):
            status, mean, std = taft.normalize( nnInputs[:,i], normInterval=[normIntervalStart,numSamples] )
            if status is None:
                logMessage += "Can't normalize %d column\n." % (i)
                return None
            nnMean[i] = mean
            nnStd[i] = std
    else:
        logMessage += "Normalization skipped.\n"
        nnMean = None
        nnStd = None

    if detachTest is None:
        retval1 = { 'inputs': nnInputs, 'labels': nnLabels, 'profit': nnProfit, 
            'numSamples':numSamples, 'numFeatures':numFeatures, 'numLabels':numLabels, 'mean':nnMean, 'std':nnStd }    
        retval2 = None
    else:
        retval1 = { 'inputs': nnInputs[detachStart:], 'labels': nnLabels[detachStart:], 'profit': nnProfit[detachStart:], 
            'numSamples':numSamples-detachStart, 'numFeatures':numFeatures, 'numLabels':numLabels, 'mean':nnMean, 'std':nnStd }    
        retval2 = { 'inputs': nnInputs[:detachStart], 'labels': nnLabels[:detachStart], 'profit': nnProfit[:detachStart], 
            'numSamples':detachStart, 'numFeatures':numFeatures, 'numLabels':numLabels, 'mean':nnMean, 'std':nnStd }    

    return( retval1, retval2 )
# end of def prepareData

__lookBack = None
__lookAhead = None

def setLookBack( lookBack ):
    global __lookBack
    __lookBack = lookBack

def setLookAhead( lookAhead ):
    global __lookAhead
    __lookAhead = lookAhead

def __calcData( pastRates, futureRates ):
    global __lookBack
    global __lookAhead
    retErr = None, None, None

    # Calculating inputs / Вычисляем "инпуты"
    if __lookBack is not None: # Какие временные отрезки "прошлого" мы будем пересчитывать в "инпуты" сети  
        lookBack = __lookBack 
    else:
        lookBack = [ [0,0], [1,1], [2,3], [4,6], [7,10] ] # По умолчанию

    inputs = []

    cl0 = pastRates['cl'][0] # "Сейчас" мы в точке '0', последняя известная цена - цена закрытия
    lenRates = len( pastRates['cl'] ) 

    for i in range( len( lookBack ) ):
        startRate = lookBack[i][0]
        endRate = lookBack[i][1]
        if endRate >= lenRates: # Если нужная нам точка лежит за пределами массива, "инпуты" подсчитать не удастся
            return retErr

        high = pastRates['hi'][startRate:endRate+1] # Массив со значениями HIGH на выбранном интервале прошлого
        highestHigh = np.max( high ) # Ищем максимальный HIGH
        inputs.append( highestHigh - cl0 ) # Добавляем "инпут"

        low = pastRates['lo'][startRate:endRate+1] # Массив со значениями LOW на выбранном интервале прошлого
        lowestLow = np.min( low ) # Ищем минимальный LOW
        inputs.append( cl0 - lowestLow ) # Добавляем "инпут"

    # Calculating labels and profits / Вычисляем "аутпуты" (labels) и ддоходность
    if __lookAhead is None: # На сколько периодов вперед надо смотреть
        ahead = 0 # По умолчанию смотрим вперед на один период, а значит нас интересует цена закрытия 0-го периода
    else:
        ahead = __lookAhead
    if ahead >= len(futureRates['cl']): # Если требуется смотреть за пределы массивов с котировками, расчет невозможен.
        return retErr

    # Вычисляем "аутпут" - отношение (CLOSE-OPEN) / (HIGH-LOW) на указанном (переменной ahead) отрезке "ближайшего будущего".
    # Каждое значения "аутпута" будет отнесено к одной из трех категорий и представлено в виде one-hot вектора длиной 3.
    # Маленькие значения будут кодироваться [1,0,0], средние - [0,1,0], большие - [0,0,1].  
    bins = 3
    op = futureRates['op'][0]
    cl = futureRates['cl'][ahead]
    hi = np.max( futureRates['hi'][:ahead+1] )
    lo = np.min( futureRates['lo'][:ahead+1] )
    clLessOp = cl - op
    hiLessLo = hi - lo
    if hiLessLo > 0:
        observed = clLessOp / hiLessLo
    else:
        observed = 0.0
    observedBin = int( float(bins) * ( (observed + 1.0) / (2.0 + 1e-10) ) )
    labels = np.zeros( shape=[bins], dtype=np.float32 )
    labels[observedBin] = 1.0

    profit = clLessOp # Позиция будет открыта "сейчас" (futureRates['op'][0]) и закрыть ее через ahead периодов (futureRates['cl'][ahead]).
                        # Доходность на этом отрезке составит CLOSE-OPEN (этого временного отрезка) 

    return inputs, labels, profit
# end of def __calcData


def saveData( fileName, data, normOnly=False ):
    global logMessage
    ok = True

    logMessage += "Saving into \"%s\"...\n" % (fileName)

    try:    
        s = shelve.open( fileName )
    except Exception:
        ok = False

    if ok:
        try:
            if not normOnly:
                s['inputs'] = data['inputs']
                s['labels'] = data['labels']
                s['profit'] = data['profit']
            s['mean'] = data['mean']
            s['std'] = data['std']
        except Exception:
            ok = False
        finally:
            s.close()

    return ok
# end of saveData()


def loadData( fileName, normOnly=False ):
    global logMessage
    ok = True

    logMessage += "Reading data from \"%s\"...\n" % (fileName)
    try:
        s = shelve.open( fileName )
    except Exception:
        ok = False
        logMessage += "Can't open file %s.\n" % (fileName)
        
    if ok:
        try:
            if not normOnly:
                data['inputs'] = s['inputs']
                data['labels'] = s['labels']
                data['profit'] = s['profit']
            data['mean'] = s['mean']
            data['std'] = s['std']
            s.close()
        except Exception:
            ok = False
            logMessage += "Error reading the data.\n"
        finally:
            s.close()

    if ok:
        return data
    else:
        return None
# end of loadData()

