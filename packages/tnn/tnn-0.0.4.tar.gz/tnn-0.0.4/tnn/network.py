# -*- coding: utf-8 -*- 
import tensorflow as tf
import numpy as np
import datetime as dt
import shelve
import os
import tnn.utils

class Network:
    # Общее число сетей
    numNetworks = 0

    '''
    numLayers - (integer, default:1) Число hidden-слоев сети
    numNodes - (list of integers, default:[10]) Число узлов в каждом слое  
    numFeatures - (integer, default:10) Размерность "инпутов" (x, они же "samples", в каждом sample присутствует numFeatures значений)
    numLabels  - (integer, default:2) Размерность "аутпутов" (y, они же "labels") заданных в формате "one-hot"
    stdDev - (float) Стандартное отклонение для первичной генерации весов сети, default: 0.03 
    activationFuncs (list, default:None) - функции активации, размерность numLayers+1 (число hidden-слоев + 1). 
        Если "None", то активация hidden-слоев будет осуществляться через relu, а output-слоя - через softmax
        Если не "None", то элемент списка может быть:
            1) строкой: "relu", "sigmoid", "softmax"
            2) непосредственно функцией активации
    weights (list of 2d numpy arrays, default:None) - список, состоящий из двумерных матриц, 
        хранящих весовые коэффициенты слоев сети. Если weights==None, весовые коэффициенты будут сгенерированы автоматически
    bs (list of 1d numpy arrays, default:None) - список, состоящий из векторов, 
        хранящих весовые bias-коэффициенты (свободные члены) сети. Если bs==None, коэффициенты будут сгенерированы автоматически
    '''
    def __init__(self, numLayers=1, numNodes=[10], numFeatures=10, numLabels=2, stdDev=0.03, activationFuncs=None, weights=None, bs=None ):
        self.numLayers = numLayers # (integer) Число hidden-слоев
        self.numNodes = numNodes # (list of integers) Число узлов в каждом слое, numNodes[0] - число слоев в первом hidden-слое 
        self.numFeatures = numFeatures # (integer) Число features, т.е. размерность "инпутов" (x0,x1,x2,...,xn).
        self.numLabels = numLabels # One-hot labels

        # placeholder для "инпутов" (размерность: numSamples x numFeatures) - x [ [0.5,0.8,0.7], [0.4,0.7,0.6], ...  ] 
        self.x = tf.placeholder( tf.float64, [ None, numFeatures ] )

        # placeholder для "аутпутов" (они же "labels", размерность numSamples x numLables) - y  [ [0,1], [1,0], ... ]   
        self.y = tf.placeholder( tf.float64, [ None, numLabels ] )

        self.weights = [] # (list of tensors) Веса всех слоев сети 
        self.bs = [] # (list of tensors) Biases всех слоев сети

        if weights is None or bs is None: # Если веса не заданы в качестве параметров функции, инициализируем соответствующие tf-переменные случайными значениями
            for i in range( numLayers ):  
                # Веса (w) + bias-столбец (b) для связи "инпутов" x и очередного hidden-слоя.
                if i == 0: # Если это первый hidden-слой, то его размерность по оси '0' равна numFeatures
                    numNodes0 = numFeatures
                else: # Если не первый слой, то его размерность по оси '0' равна размерности предыдущего по оси '1'
                    numNodes0 = numNodes[i-1]
                w = tf.Variable( tf.random_normal( [ numNodes0, numNodes[i] ], stddev=stdDev, dtype=tf.float64 ), 
                    name='W'+str(i), trainable=True )
                b = tf.Variable( tf.random_normal( [ numNodes[i] ], dtype=tf.float64 ), 
                    name='b'+str(i), trainable=True )
                self.weights.append(w)
                self.bs.append(b)            
            # Веса (w) + bias column (b) для связи hidden-слоя и output-слоя. 
            w = tf.Variable( tf.random_normal( [ numNodes[numLayers-1], numLabels ], stddev=stdDev, dtype=tf.float64 ), 
                name='W'+str(numLayers), trainable=True )
            b = tf.Variable( tf.random_normal( [ numLabels ], dtype=tf.float64 ), 
                name='b'+str(numLayers), trainable=True )
            self.weights.append(w)
            self.bs.append(b)
        else: # Если веса заданы в качестве параметров функции, инициализируем ими соотетствующие tf-переменные
            for i in range( numLayers+1 ):
                w = tf.Variable( weights[i], dtype=tf.float64, name='W'+str(i), trainable=True )
                b = tf.Variable( bs[i], dtype=tf.float64, name='b'+str(i), trainable=True )
                self.weights.append(w)
                self.bs.append(b)

        self.activationFuncs = activationFuncs # Функции активации для каждого слоя

        self.learnDir = "" # На этапе обучения в эту переменную будет записана строка, сформированная из текущих даты и времени

        self.profit = tf.placeholder( tf.float64, [ None ] ) # Доходность для рассчета прибыльности во время обучения и тестирования

        Network.numNetworks += 1 # Увеличиваем счетчик сетей на 1.
    # end of __init__

    '''
    x (2d numpy array, np.float64) - "инпуты" (samples) для обучения сети, размерность numSamples x numFeatures -> в placeholder self.x
    y (2d numpy array, np.float64) - "аутпуты" (labels) для обучения сети, размерность numSamples x numLabels -> в placeholder self.y
    profit (1d numpy array, np.float64, default: None) - значения прибыли (убытка) по каждому sample, 
        размерность: numSamples (как в x и y)
    xTest (2d numpy array, np.float64, default:None) - "инпуты" (samples) для тестирования сети, размерность: numSamples x numFeatures 
    yTest (2d numpy array, np.float64, default:None) - "аутпуты" (labels) для тестирования сети, размерность: numSamples x numLabels
    profitTest (1d numpy array, np.float64, default: None) - значения прибыли (убытка) по каждому sample, 
        размерность: numSamples (как в xTest и yTest)
    shortTradesHaveNegativeProfit (boolean, default:True) - указывает на знак величин в массивах profit и profitTest.
        Если True, то прибыль по сделкам SHORT должна быть задана в этих массивах отрицательным числом, а 
        если False - то положительным.
    learningRate (float, default:0.05) - self explained 
    numEpochs (int, defaul:1000) - self explained
    balancer (float, default:0.0) - если balancer > 0.0, то при вычислении cost-функции совпадение/несовпадение по последнему 
        бину получит весовой коэффициент (balancer+1.0), в то время как по остальным бинам коэффициент будет 1.0.
    optimizer (string или func, default:None) - способ оптимизации. Если "None", то используется GradientDescentOptimizer. 
        Если не "None", то способ оптимизации может быть задан:
            1) строкой (возможны только: "GradientDescent", "Adadelta", "Adagrad", "Adam", "Ftrl", "RMSProp" и т.д.)
            2) напрямую объектом, например: tf.train.GradientDescentOptimizer(learning_rate=0.01) 
    prognoseProb (float, default:None) - пороговое значение оценки вероятности.
        При превышении этого значения "аутпутом" (y) в последнем ("торгующем") бине мы считаем, что сеть дает сигнал на сделку. 
        Если prognoseProb==None, по сигнал на сделку дается, если значение "аутпута" в последнем бине больше, 
        чем значения в остальных бинах. 
    summaryDir (string, default:None) - папка, куда tensorflow пишет summary ("отчет"). 
        Если summaryDir==None, отчеты записываться не будут.
        Если summaryDir=="", то имя папки будет сгенерировано автоматически из текущих даты и времени (только числа, без других знаков).
    printRate (int, default:20) - частота, с которой во время обучения на терминал выводятся параметры обучения и тестирования сети
        (значение cost-функции, точность (accuracy), баланс (если задан на входе)).
        Если printRate=="None", то вывода параметров не будет
    learnIndicators (boolean, default:False) - если задать True, в процессе обучения, для каждой эпохи будут записываться
        пары значений (для train и test данных): 
        - cost-функция на тест vs cost-функция на train
        - точность (accuracy) на тест vs точность (accuracy) на train
        - доходность на тест vs доходность на train.
        По этим парам значений можно будет построить регрессионную зависимость.
    saveRate (integer, default:None) - задает как часто надо сохранять веса сети в процессе обучения.
        Веса сохраняются в папку saveDir (см. ниже) в файл, имя которого состоит из номера эпохи и
        текущих значений: cost-функции (см. переменную cost в теле функции), 
        точности модели (см. переменную accuracy) и прибыльности (см. переменную profit)  
        Если saveRate==None, веса не сохраняются.
        Сохраненные веса можно прочитать функцией loadТNetwork().
    saveDir (string, default:None) - задает имя папки, в которую будет сохраннен файл с весами сети.
        Если saveDir==None, имя папки будет сгенерировано на основе текущих даты и времени.
    '''
    def learn( self, x, y, profit=None, xTest=None, yTest=None, profitTest=None, 
        learningRate=0.05, numEpochs=1000, balancer=0.0, autoBalancers=False, optimizer=None, numBatches=1,
        tradingLabel=None, shortTradesHaveNegativeProfit=True, flipOverTrading=False, prognoseProb=None, 
        summaryDir=None, printRate=20, learnIndicators=False, saveRate=None, saveDir=None):

        # Время запуска сеанса обучения в виде текстовой строки. Будет использоваться для создания папок с отчетами 
        self.learnDir = dt.datetime.now().strftime("%Y%m%d%H%M%S")

        # Создаем tf-операции вычислени "аутпута" (в матмодели это 'y') сети
        yOp = self.__createNetworkOutputOp()
    
        # Все значения меньше 1e-10 превращаем в 1e-10, все значения больше 0.99999999 превращаем в 0.99999999: 
        yClippedOp = tf.clip_by_value( yOp, 1e-10, 0.99999999 )

        # Операция tradesPrognosedOp возвращает 1-мерный массив длиной numSamples: 
        # '1.0', если для данного набора "инпутов" был предсказан последний бин (т.е. сигнал на сделку LONG) 
        # '-1.0', если для данного набора "инпутов" был предсказан первый бин (т.е. сигнал на сделку SHORT)
        # '0', если торговых сигналов не было.
        if tradingLabel is not None: # Если задан "торговый" бин (label) - 0-й или 'numLabels-1'-й
            if prognoseProb is None:
                isTradingLabelPrognosedOp = tf.equal( tf.argmax( yOp,1 ), tradingLabel )
            else:
                isTradingLabelPrognosedOp = tf.greater( yOp[:,tradingLabel], prognoseProb )
            tradesPrognosedOp = tf.cast( isTradingLabelPrognosedOp, tf.float64 )
            if tradingLabel == 0:
                tradesPrognosedOp = -1.0 * tradesPrognosedOp
        else: # Если торговый бин не указан, то предполагается, что сеть торгует по первому (SHORT) и последнему (LONG) бинам 
            if prognoseProb is None: 
                isFirstLabelPrognosedOp = tf.equal( tf.argmax( yOp,1 ), 0 )
                isLastLabelPrognosedOp = tf.equal( tf.argmax( yOp,1 ), self.numLabels-1 )
                tradesPrognosedOp = -1.0 * tf.cast( isFirstLabelPrognosedOp, tf.float64 ) + \
                    1.0 * tf.cast( isLastLabelPrognosedOp, tf.float64 )
            else: # Если указана прогнозная вероятность:
                isFirstOp = tf.greater( yOp[:,0], prognoseProb )
                isLastOp = tf.greater( yOp[:,self.numLabels-1], prognoseProb )
                isFirstGreaterOp = tf.greater( yOp[:,0], yOp[:,self.numLabels-1] )
                isLastGreaterOp = tf.greater( yOp[:,self.numLabels-1], yOp[:,0] )
                isFirstLabelPrognosedOp = tf.logical_and( isFirstOp, isFirstGreaterOp )
                isLastLabelPrognosedOp = tf.logical_and( isLastOp, isLastGreaterOp)
                tradesPrognosedOp = -1.0 * tf.cast( isFirstLabelPrognosedOp, tf.float64 ) + \
                    1.0 * tf.cast( isLastLabelPrognosedOp, tf.float64 )

        # Cost-функция (costOp).
        # Если переменная balancer > 0.0, cost-функция будет учитывать "торговый" бин(ы) с бОльшим весом
        # Если задана опция "autoBalance", будет рассчитано число элементов по каждому label; эти даннные будут учтены
        # при рассчете cost-функции.
        numSamplesOp = tf.shape(self.y)[0]
        if balancer > 0.0 and tradingLabel is not None: 
            balancerOnesOp = tf.ones( [ numSamplesOp, self.numLabels-1 ], dtype=tf.float64 )
            #tf.reshape( tf.cast(isTradingLabelPrognosedOp,tf.float64) * balancer, [numSamplesOp,1] )
            balancerVectorOp = tf.ones( [numSamplesOp,1], dtype=tf.float64 ) + balancer
            if tradingLabel == self.numLabels-1:
                balancerOp = tf.concat( [ balancerOnesOp, balancerVectorOp ], 1 )
            else:
                balancerOp = tf.concat( [ balancerVectorOp, balancerOnesOp ], 1 )
        elif balancer > 0.0 and tradingLabel is None: # The balancer for trading labels is given as a parameter of the function 
            balancerOnesOp = tf.ones( [ numSamplesOp, self.numLabels-2 ], dtype=tf.float64 )
            #balancerFirstVectorOp = tf.reshape( tf.cast( isFirstLabelPrognosedOp, tf.float64 )*balancer, [numSamplesOp,1] )
            balancerFirstVectorOp = tf.ones( [numSamplesOp,1], dtype=tf.float64 )
            balancerFirstVectorOp = balancerFirstVectorOp + balancer 
            #balancerLastVectorOp = tf.reshape( tf.cast( isLastLabelPrognosedOp, tf.float64 )*balancer, [numSamplesOp,1] )
            balancerLastVectorOp = tf.ones( [numSamplesOp,1], dtype=tf.float64 )
            balancerLastVectorOp = balancerLastVectorOp + balancer 
            balancerOp = tf.concat( [ balancerFirstVectorOp, balancerOnesOp, balancerLastVectorOp ], 1 )
        elif balancer == 0.0 and tradingLabel is None and autoBalancers == True: # The auto-balance operation should be done
            countsOfLabelsOp = tf.reduce_sum( self.y, 0 ) # Число обучающих примеров для каждого label
            # Элементы (веса) balancerRow обратно пропорциональны числу примеров для каждого label: 
            balancerRow = (tf.cast(numSamplesOp,tf.float64) - countsOfLabelsOp) / tf.cast(numSamplesOp,tf.float64)
            # Делаем матрицу весов balancerOp для умножения на нее составляющих сost-функции
            balancerTiledOp = tf.tile( balancerRow, [ numSamplesOp ] )
            balancerOp = tf.reshape( balancerTiledOp, [ numSamplesOp, self.numLabels ] )
        else: 
            balancerOp = tf.ones( [numSamplesOp, self.numLabels], dtype=tf.float64 )
        costOp = -tf.reduce_mean( 
            tf.reduce_sum( self.y * tf.log(yClippedOp) * balancerOp + (1.0 - self.y) * tf.log(1.0 - yClippedOp) * balancerOp, axis=1 ) )

        # Оптимизатор. Если None, то используем GradientDescentOptimizer
        if optimizer is None:
            optimiserOp = tf.train.GradientDescentOptimizer( learning_rate=learningRate ).minimize( costOp )
        elif isinstance( optimizer, str ):
            optimiserOp = utils.getOptimizer( optimizer, learningRate ).minimize( costOp )
        elif isinstance( optimizer, object ): # Оптимизатор задан напрямую
            optimiserOp = optimizer.minimize( costOp )

        # Операции для вычисления доходности ( finalBalanceOp )
        if tradingLabel == 0 and shortTradesHaveNegativeProfit == False:
            profitByTrades = tf.multiply( tf.abs(tradesPrognosedOp), self.profit )
        elif flipOverTrading:
            flipOverTradesOp = self.__flipOverTrades( tradesPrognosedOp )
            profitByTrades = tf.multiply( flipOverTradesOp, self.profit )
        else:
            profitByTrades = tf.multiply( tradesPrognosedOp, self.profit )            
        finalBalanceOp = tf.reduce_sum( profitByTrades )  

        # Операции для оценки общей точности модели. Общая точность оценивается по числу совпадений предсказаний по ВСЕМ бинам
        accuracyOp = tf.reduce_mean( tf.cast( tf.equal( tf.argmax(self.y, 1), tf.argmax(yOp, 1) ), tf.float64 ) )

        # Вычисление "торговой" точности (tradeAccuracyOp) - учитываются ТОЛЬКО предсказания по "торговому(ым)" бину(ам) 
        if tradingLabel is not None:
            isTradingLabelOccuredOp = tf.equal( self.y[:,tradingLabel], 1.0 )
            isTradingLabelPrognosedAndOccuredOp = tf.logical_and( isTradingLabelPrognosedOp, isTradingLabelOccuredOp )
            prognosedAndOccuredSumOp = tf.reduce_sum( tf.cast( isTradingLabelPrognosedAndOccuredOp, tf.float64 ) )
            prognosedSumOp = tf.reduce_sum( tf.cast( isTradingLabelPrognosedOp, tf.float64 ) )
        else:
            isFirstLabelOccuredOp = tf.equal( self.y[:,0], 1.0 )
            isFirstLabelPrognosedAndOccuredOp = tf.logical_and( isFirstLabelPrognosedOp, isFirstLabelOccuredOp )
            isLastLabelOccuredOp = tf.equal( self.y[:,self.numLabels-1], 1.0 ) 
            isLastLabelPrognosedAndOccuredOp = tf.logical_and( isLastLabelPrognosedOp, isLastLabelOccuredOp )
            prognosedAndOccuredSumOp = tf.reduce_sum( tf.cast( isFirstLabelPrognosedAndOccuredOp, tf.float64 ) ) + \
                tf.reduce_sum( tf.cast( isLastLabelPrognosedAndOccuredOp, tf.float64 ) )
            prognosedSumOp =  tf.reduce_sum( tf.cast( isFirstLabelPrognosedOp, tf.float64 ) ) + \
                tf.reduce_sum( tf.cast( isLastLabelPrognosedOp, tf.float64 ) )
        tradeAccuracyNonZeroOp = lambda: tf.divide( prognosedAndOccuredSumOp, prognosedSumOp )
        tradeAccuracyZeroOp = lambda: tf.constant( 0.0, dtype=tf.float64 )
        tradeAccuracyOp = tf.cond( tf.not_equal( prognosedSumOp, 0.0 ), tradeAccuracyNonZeroOp, tradeAccuracyZeroOp )

        # Вычисление числа сделок (tradesNumOp)
        if flipOverTrading == False:
            tradesNumOp = self.__tradesNum( tradesPrognosedOp )
        else:
            tradesNumOp = self.__flipOverTradesNum( flipOverTradesOp )

        # Для summary
        if summaryDir is not None:
            accuracySumm = tf.summary.scalar( 'Accuracy (Train)', accuracyOp )
            costSumm = tf.summary.scalar( 'Cost (Train)', costOp )
            if profit is not None:
                balanceSumm = tf.summary.scalar( 'Profit (Train)', finalBalanceOp )
            if xTest is not None and yTest is not None:
                accuracyTestSumm = tf.summary.scalar( 'Accuracy (Test)', accuracyOp )
                costTestSumm = tf.summary.scalar( 'Cost (Test)', costOp )
                if profitTest is not None:
                    balanceTestSumm = tf.summary.scalar( 'Final Balance (Test)', finalBalanceOp )

            # Если папка для summary == "", имя папки будет состоять из сегодняшней даты и времени (только числа, без других знаков) 
            if summaryDir == "":
                summaryDir = self.learnDir + "_" + "summary"
            writer = tf.summary.FileWriter( summaryDir )

        # !!!!FOR DEBUGGING PURPOSES ONLY!!!!
        #utils.log( "X:\n" + str(x) )
        #utils.log( "Y:\n" + str(y) )

        # Запускаем сессию
        with tf.Session() as sess:
            # Инициализируем переменные
            sess.run( tf.global_variables_initializer() )

            # Исходные данные: для обучения (train) и тестирования (test)
            feedDict, feedDictTest = self.__initFeedDicts( x, y, profit, xTest, yTest, profitTest, 1, 1 ) 

            # Если указано считать регрессионную зависимость между показателями сети на train и test, 
            # инициализируем массивы для хранения соответствующих данных
            if learnIndicators:
                self.__initLearnIndicators( numEpochs )

            # Запускаем обучение 
            for epoch in range(numEpochs):

                epochLog = "" # Текстовая строка, которая будет выведена в лог

                # numBatches = 10
                if numBatches > 1: # Запускаем поэтапную оптимизации сети, предварительно разбив samples на "пакеты".
                    for i in range(numBatches):
                        feedDictBatched, _ = self.__initFeedDicts( x, y, profit, None, None, None, numBatches, i+1 )
                        sess.run(optimiserOp, feed_dict = feedDictBatched )                    
                else:
                    sess.run(optimiserOp, feed_dict = feedDict ) # Запускаем операцию оптимизации сети для samples сразу
                
                # Вычисляем переменные - показатели функционирования сети на обучающих (train) данных: значение cost-функици, 
                # точность прогнозов по ВСЕМ бинам (accuracy) и точность прогнозов по ПОСЛЕДНЕМУ бину (tradeAccuracy)
                cost, accuracy, tradeAccuracy, tradesNum = \
                    sess.run( [costOp, accuracyOp, tradeAccuracyOp, tradesNumOp], feed_dict = feedDict )

                # !!!!FOR DEBUGGING PURPOSES ONLY!!!!
                #utils.log( sess.run(yOp, feed_dict=feedDict) )
                #utils.log( self.weights )

                # Если передан массив с данными по доходности сделок - вычисляем доходность, которую дала бы сеть, 
                # торгуя на обучающих (train) данных.
                if profit is not None:
                    finalBalance = sess.run( finalBalanceOp, feed_dict = feedDict )
                else:
                    finalBalance = 0.0

                if summaryDir is not None: # Формируем summary - "отчет" tensorflow
                    writer.add_summary( sess.run( accuracySumm, feed_dict = feedDict ), epoch )
                    writer.add_summary( sess.run( costSumm, feed_dict = feedDict ), epoch )
                    if profit is not None:
                        writer.add_summary( sess.run( balanceSumm, feed_dict = feedDict ), epoch )

                # Строка, которая будет выведена в лог
                epochLog += "Epoch: %d/%d: cost:%4g %%=%d trade%%:%d $:%g (%d)" % \
                    ( epoch+1, numEpochs, cost, np.int(accuracy*100.0), np.int(tradeAccuracy*100.0), finalBalance, tradesNum )

                # Если переданы тестовые данные, вычисляем показатели функционирования сети на них
                if xTest is not None and yTest is not None:
                    # Вычисляем переменные-показатели функционирования сети на тестовых (test) данных: значение cost-функици, 
                    # точность прогнозов по ВСЕМ бинам (accuracy) и точность прогнозов по ПОСЛЕДНЕМУ бину (tradeAccuracy)
                    costTest, accuracyTest, tradeAccuracyTest, tradesNumTest = \
                        sess.run( [costOp, accuracyOp, tradeAccuracyOp, tradesNumOp], feed_dict = feedDictTest )

                    # Если передан массив с данными по доходности сделок - вычисляем доходность, которую дала бы сеть, 
                    # торгуя на тестовых (test) данных.
                    if profitTest is not None:
                        finalBalanceTest = sess.run( finalBalanceOp, feed_dict = feedDictTest )    
                    else:
                        finalBalanceTest = 0.0

                    # FOR DEBUGGING PURPOSES ONLY!!!!
                    '''
                    if epoch % printRate == 0:
                        logValues = sess.run( tradesPrognosedOp, feed_dict = feedDictTest )
                        logStr = ""
                        logSum = 0
                        for logValue in range( len(logValues) ):
                            logStr += str(int(logValues[logValue])) + "x" + str( profitTest[logValue] ) + " "
                            logSum += int(logValues[logValue]) * profitTest[logValue]
                        utils.log( logStr ) 
                        utils.log( logSum ) 
                    '''
                    # FOR DEBUGGING PURPOSES ONLY!!!!

                    if summaryDir is not None: # Формируем summary - "отчет" tensorflow
                        writer.add_summary( sess.run( accuracyTestSumm, feed_dict = feedDictTest ), epoch )
                        writer.add_summary( sess.run( costTestSumm, feed_dict = feedDictTest ), epoch )
                        if profitTest is not None:
                            writer.add_summary( sess.run( balanceTestSumm, feed_dict = feedDictTest ), epoch )

                    # Строка, которая будет выведена в лог
                    epochLog += "  TEST: cost:%4g %%:%d trade%%:%d $:%g (%d)" % \
                        (costTest, np.int(accuracyTest*100.0), np.int(tradeAccuracyTest*100.0), finalBalanceTest, tradesNumTest)
    
                # Добавляем перевод строки
                self.__printEpochLog( printRate, epoch, epochLog )

                if learnIndicators:
                    self.__addLearnIndicators( epoch, cost, costTest, accuracy, accuracyTest, 
                        tradeAccuracy, tradeAccuracyTest, finalBalance, finalBalanceTest )

                # Сохраняем веса сети (сохранение будет выполнено, если saveRate is not None) 
                self.__saveEpoch( sess, saveRate, saveDir, epoch, numEpochs, cost, accuracy, finalBalance )

            print("\nDone!")

            if summaryDir is not None:
                writer.add_graph(sess.graph)
        # end of with tf.Session() as sess
    # end of learn()

    def __createNetworkOutputOp( self ):
        inputMatrix = self.x
        for i in range( self.numLayers ):
            # Вычисление (активация) hidden-слоя
            inputMatrix = tf.add( tf.matmul( inputMatrix, self.weights[i] ), self.bs[i] )
            if self.activationFuncs is None: # Если функция активации не задана, используем relu
                inputMatrix = tf.nn.relu( inputMatrix )
            else:
                activationFunc = utils.getActivationFunc( self.activationFuncs, i ) 
                inputMatrix = activationFunc( inputMatrix )

        # Операция для вычисления "выхода" сети
        outputMatrix = tf.add( tf.matmul( inputMatrix, self.weights[self.numLayers] ), self.bs[self.numLayers] )
        if self.activationFuncs is None: 
            outputOp = tf.nn.softmax( outputMatrix )
        else:
            activationFunc = utils.getActivationFunc( self.activationFuncs, self.numLayers, outputLayer=True ) 
            outputOp = activationFunc( outputMatrix )
        return outputOp
    # end of def

    def __initLearnIndicators( self, numEpochs ):
        self.costTrain = np.zeros( shape=[numEpochs], dtype=np.float32)  
        self.costTest = np.zeros( shape=[numEpochs], dtype=np.float32 )  
        self.accuracyTrain = np.zeros( shape=[numEpochs], dtype=np.float32 )  
        self.accuracyTest = np.zeros( shape=[numEpochs], dtype=np.float32 )  
        self.tradeAccuracyTrain = np.zeros( shape=[numEpochs], dtype=np.float32 )  
        self.tradeAccuracyTest = np.zeros( shape=[numEpochs], dtype=np.float32 )  
        self.balanceTrain = np.zeros( shape=[numEpochs], dtype=np.float32 )  
        self.balanceTest = np.zeros( shape=[numEpochs], dtype=np.float32 )  
    # end of def

    def __addLearnIndicators( self, epoch, costTrain, costTest, accuracyTrain, accuracyTest, 
        tradeAccuracyTrain, tradeAccuracyTest, balanceTrain, balanceTest ):
        self.costTrain[epoch] = costTrain
        self.costTest[epoch] = costTest
        self.accuracyTrain[epoch] = accuracyTrain
        self.accuracyTest[epoch] = accuracyTest
        self.tradeAccuracyTrain[epoch] = tradeAccuracyTrain
        self.tradeAccuracyTest[epoch] = tradeAccuracyTest
        self.balanceTrain[epoch] = balanceTrain
        self.balanceTest[epoch] = balanceTest
    # end of def

    def __saveEpoch( self, sess, saveRate, saveDir, epoch, numEpochs, cost, accuracy, finalBalance ):
        ok = True
        if saveRate is not None:
            if epoch % saveRate == 0 or epoch == numEpochs-1:
                if saveDir is None:
                    saveDir = self.learnDir
                if not os.path.exists( saveDir ):
                    try:
                        os.mkdir( saveDir )
                    except Exception:
                        ok = False
                if ok:
                    fileName = "%d_c_%.4g_a_%.4g_p_%.4g" % ( epoch, cost, accuracy, finalBalance ) 
                    path = os.path.join( saveDir, fileName ) 
                    ok = self.__save( sess, path )
        return ok                 
    #end of def

    def __printEpochLog( self, printRate, epochNum, epochLog ):
        if printRate is not None:
            if epochNum % printRate == 0:
                print( epochLog )
    # end of def

    # Инициализирует словари для операций с тензорами - train и test. 
    # При необходимости (если numBatches > 1) выделяет из выборки подвыборку (batch). 
    def __initFeedDicts( self, x, y, profit, xTest, yTest, profitTest, numBatches, batchNum ):

        xBatched, yBatched, profitBatched = self.__getBatches( x, y, profit, batchNum, numBatches )
        feedDict = { self.x: xBatched, self.y: yBatched, self.profit: profitBatched }
        
        xBatched, yBatched, profitBatched = self.__getBatches( xTest, yTest, profitTest, batchNum, numBatches )
        feedDictTest = { self.x: xBatched, self.y: yBatched, self.profit: profitBatched }

        return feedDict, feedDictTest

    # Выделяет из массивов x, y и profit подвыборку (batch).
    # Если numBatches == 1, возвращает те же самые массивы x, y и profit.
    def __getBatches( self, x, y, profit, numBatches, batchNum ):
        if numBatches > 1 and x is not None:
            numSamples = np.shape(x)[0]
            batchStart = int( (batchNum-1) * numSamples / numBatches )
            batchEnd = int( float(batchNum) * numSamples / numBatches )
        if x is not None:
            if numBatches == 1:
                xBatched = x
            else:
                xBatched = x[batchStart:batchEnd:]
        else:
            xBatched = []
        if y is not None:
            if numBatches == 1:
                yBatched = y
            else:
                yBatched = y[batchStart:batchEnd:]
        else:
            yBatched = []
        if profit is not None:
            if numBatches == 1:
                profitBatched = profit
            else:                
                profitBatched = profit[batchStart:batchEnd]
        else:
            profitBatched = []
        return xBatched, yBatched, profitBatched

    # Сохраняет веса сети в файл fileName.
    # Возвращает True в случае успеха и False в случае ошибки.  
    def __save( self, sess, fileName ):
        ok = True
        try:
            s = shelve.open( fileName )
        except Exception:
            ok = False

        if ok:
            try:
                s['weights'] = sess.run( self.weights )
                s['bs'] = sess.run( self.bs )
                s['activationFuncs'] = self.activationFuncs
            except Exception:
                ok = False
            finally:
                s.close()

        return ok       
    # end of def


    # Возвращает операцию, создающую вектор из сделок для системы торговли с "переворотом"
    # (если сеть не прогнозирует сделку, то при наличии открытой сделки мы ее не закрываем, а оставляем открытой).
    # Если элемент _tradesPrognosedOp равен '0', а перед этим было '1', то в новом векторе '0' превратится в '1'
    # Если элемент _tradesPrognosedOp равен '0', а перед этим было '-1', то в новом векторе '0' превратится в '-1'
    def __flipOverTrades( self, _tradesPrognosed ):

        def cond( i, v ):
            return i > 0

        def body( i, v ):
            makeIt1 = tf.logical_and( tf.equal( v[i], 1.0 ), tf.equal( v[i-1], 0.0 ) )
            makeItMinus1 = tf.logical_and( tf.equal( v[i], -1.0 ), tf.equal( v[i-1], 0.0 ) )

            v = tf.case( { makeIt1: lambda: tf.concat( [ v[0:i-1], [1.0], v[i:] ], 0 ), 
                makeItMinus1: lambda: tf.concat( [ v[0:i-1], [-1.0], v[i:] ], 0 ) }, 
                default=lambda: v, exclusive=True  )

            return tf.subtract(i,1), v

        n = tf.subtract( tf.shape(_tradesPrognosed)[0], 1 )
        return tf.while_loop( cond, body, loop_vars=[n,_tradesPrognosed], shape_invariants = [n.get_shape(), tf.TensorShape([None])] )[1]
    # end of def

    ''' Old version
    def __flipOverTrades( self, _tradesPrognosedOp ):

        vPrev = _tradesPrognosedOp[:-1]
        vNext = _tradesPrognosedOp[1:]
        
        isAdd = tf.logical_and( tf.equal(vPrev, 1.0), tf.equal(vNext, 0.0) )
        isAdd = tf.concat( [ [False], isAdd ], 0 )

        flipOverTradesOp = tf.add( _tradesPrognosedOp, 1.0 * tf.cast( isAdd, tf.float64 ) )

        isSubtract = tf.logical_and( tf.equal(vPrev, -1.0), tf.equal(vNext, 0.0) )
        isSubtract = tf.concat( [ [False], isSubtract ], 0 )

        flipOverTradesOp = tf.subtract( flipOverTradesOp, 1.0 * tf.cast( isSubtract, tf.float64 ) )

        return flipOverTradesOp
    '''

    # Возвращает операцию, вычисляющую число сделок
    def __tradesNum( self, _tradesPrognosedOp ):
        numTradesOp = tf.reduce_sum( tf.cast( tf.not_equal(_tradesPrognosedOp,0), tf.int32 ) )
        return numTradesOp

    # Возвращает операцию, вычисляющую число сделок для торговли с переворотом
    def __flipOverTradesNum( self, _flipOverTradesOp ):
        vectorPrev = _flipOverTradesOp[:-1]
        vectorNext = _flipOverTradesOp[1:]
        numTradesOp = tf.reduce_sum( tf.cast( tf.not_equal( vectorPrev, vectorNext ), tf.int32 ) )
        numTradesOp = tf.add( numTradesOp, tf.cast( tf.not_equal( _flipOverTradesOp[0], 0 ), tf.int32 ) )
        return numTradesOp


    # Вычисляет "аутпут" (ответ, он же 'y') сети
    # x (1d numpy array, np.float) - "инпут", размерность: numFeatures [x0,x1,...,xn]
    # Возвращает 1d numpy array размерностью numLables (это число задается при создании сети - см. конструктор) 
    def calcOutput( self, x ):
        output = None

        outputOp = self.__createNetworkOutputOp()
        
        with tf.Session() as sess:

            sess.run( tf.global_variables_initializer() )
            if len( np.shape(x) == 1 ): # Если подан 1-d array (нужен рассчет для одной точки) - преобразуем его в 2-d
                # x = [x]
                x = np.reshape( x, [1,self.numFeatures] )
            output = sess.run( outputOp, feed_dict = { self.x: x } )

        return output
    # end of def
    def calcOutputs( self, x ):
        output = None

        outputOp = self.__createNetworkOutputOp()
        
        with tf.Session() as sess:

            sess.run( tf.global_variables_initializer() )
            output = sess.run( outputOp, feed_dict = { self.x: x } )

        return output
    # end of def


# end of class
