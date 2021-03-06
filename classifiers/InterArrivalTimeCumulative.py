# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import wekaAPI
import arffWriter

from statlib import stats

from Trace import Trace
from Packet import Packet
import math

import numpy as np
from sklearn.decomposition import PCA

import config
from Utils import Utils

import theano_dir.dA_2 as dA_2
import theano_dir.SdA_2 as SdA_2
import theano_dir.logistic_sgd_2 as logistic_sgd_2
import theano_dir.mlp_2 as mlp_2
import theano_dir.mlp_3 as mlp_3
import theano_dir.SdA_3 as SdA_3
import theano_dir.LeNetConvPoolLayer_2 as LeNetConvPoolLayer_2

class InterArrivalTimeCumulative:

    @staticmethod
    def traceToInstance( trace ):

        instance = {}

        cumTimeIntervalSum = 0

        cumTimeIntervalSumList = []

        prevUp = None
        prevDn = None

        for packet in trace.getPackets():

            if prevUp == None and packet.getDirection() == Packet.UP:  # first uplink packet
                prevUp = packet
                continue

            if prevDn == None and packet.getDirection() == Packet.DOWN:  # first downlink packet
                prevDn = packet
                continue

            if packet.getDirection() == Packet.UP:
                currUp = packet

                timeInt = float(currUp.timeStr) - float(prevUp.timeStr)

                # for d 7 dataset, gathering interarrival times and coutning them,
                # saved later to a file in mainBiDirectionLatest2.py
                if not config.INTER_PACKET_ARRIVAL_HISTO_UP.get(timeInt):
                    config.INTER_PACKET_ARRIVAL_HISTO_UP[timeInt] = 0
                config.INTER_PACKET_ARRIVAL_HISTO_UP[timeInt] += 1

                prevUp = currUp
            else:
                currDn = packet

                timeInt = float(currDn.timeStr) - float(prevDn.timeStr)

                # for d 7 dataset, gathering interarrival times and coutning them,
                # saved later to a file in mainBiDirectionLatest2.py
                if not config.INTER_PACKET_ARRIVAL_HISTO_DN.get(timeInt):
                    config.INTER_PACKET_ARRIVAL_HISTO_DN[timeInt] = 0
                config.INTER_PACKET_ARRIVAL_HISTO_DN[timeInt] += 1

                prevDn = currDn

            cumTimeIntervalSum += timeInt

            cumTimeIntervalSumList.append(cumTimeIntervalSum)

        i = 0
        for timeInt in cumTimeIntervalSumList:

            instance[str(i)] = timeInt

            # take the first x features and other random ones
            #if (i < 20) or (i in config.RANDOM_LIST):
            #    instance[str(i)] = timeInt

            i += 1
            #if i > 1000:
            #    break

        instance['class'] = 'webpage'+str(trace.getId())

        return instance

    '''
    @staticmethod
    def traceToInstanceOld( trace ):

        instance = {}

        cumTimeIntervalSum = 0

        cumTimeIntervalSumList = []

        prev = None

        direction = None

        for packet in trace.getPackets():

            if prev == None or direction == None: # first packet
                prev = packet
                direction = packet.getDirection()
                continue

            curr = packet

            timeInt = float(curr.timeStr) - float(prev.timeStr)

            # for d 7 dataset, gathering interarrival times and coutning them,
            # saved later to a file in mainBiDirectionLatest2.py
            #if not config.INTER_PACKET_ARRIVAL_HISTO.get(timeInt):
            #   config.INTER_PACKET_ARRIVAL_HISTO[timeInt] = 0
            #config.INTER_PACKET_ARRIVAL_HISTO[timeInt] += 1

            prev = curr

            cumTimeIntervalSum += timeInt

            cumTimeIntervalSumList.append(cumTimeIntervalSum)

        i = 0
        for timeInt in cumTimeIntervalSumList:

            instance[str(i)] = timeInt

            # take the first x features and other random ones
            #if (i < 20) or (i in config.RANDOM_LIST):
            #    instance[str(i)] = timeInt

            i += 1
            #if i > 1000:
            #    break


        instance['class'] = 'webpage'+str(trace.getId())

        return instance
    '''

    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )
        [trainingFileOrig, testingFileOrig] = [trainingFile,testingFile]

        if config.NUM_MONITORED_SITES != -1: #no need to classify as this is for generating openworld datasets. See the line above (arffWriter)
            [accuracy,debugInfo] = ['NA', []]
            return [accuracy,debugInfo]

        if config.n_components_PCA != 0:
            [trainingFile,testingFile] = Utils.calcPCA2([trainingFile,testingFile])

        if config.n_components_LDA != 0:
            [trainingFile,testingFile] = Utils.calcLDA4([trainingFile,testingFile])

        if config.n_components_QDA != 0:
            [trainingFile,testingFile] = Utils.calcQDA([trainingFile,testingFile])

        if config.lasso != 0:
            #[trainingFile,testingFile] = Utils.calcLasso3([trainingFile,testingFile])
            #[trainingFile,testingFile] = Utils.calcLogisticRegression([trainingFile,testingFile])
            Utils.calcLogisticRegression([trainingFile,testingFile])

        # deep learning
        if config.DEEP_LEARNING_METHOD != -1:
            #[trainingFile, testingFile] = dA_2.calcAE([trainingFile, testingFile]) # one layer dA
            #[trainingFile, testingFile] = dA_2.calcAE([trainingFile, testingFile]) # two layers dA
            #[trainingFile, testingFile] = dA_2.calcAE([trainingFile, testingFile])
            #SdA_2.calcSdA([trainingFile, testingFile])
            if config.DEEP_LEARNING_METHOD == 1:
                [trainingFile, testingFile] = logistic_sgd_2.runDL([trainingFile, testingFile])
            elif config.DEEP_LEARNING_METHOD == 2:
                [trainingFile, testingFile] = dA_2.runDL([trainingFile, testingFile])
                [trainingFile, testingFile] = dA_2.runDL([trainingFile, testingFile])
                #[trainingFile, testingFile] = dA_2.runDL([trainingFile, testingFile])
                #[trainingFile, testingFile] = dA_2.runDL([trainingFile, testingFile])
                #[trainingFile, testingFile] = dA_2.runDL([trainingFile, testingFile])
            elif config.DEEP_LEARNING_METHOD == 3:
                # DL classifier
                return mlp_2.runDL([trainingFile, testingFile])
            elif config.DEEP_LEARNING_METHOD == 4:
                return SdA_2.runDL([trainingFile, testingFile])
            elif config.DEEP_LEARNING_METHOD == 5:
                return mlp_3.runDL([trainingFile, testingFile])
            elif config.DEEP_LEARNING_METHOD == 6:
                return SdA_3.runDL([trainingFile, testingFile])
            elif config.DEEP_LEARNING_METHOD == 7:
                return LeNetConvPoolLayer_2.runDL([trainingFile, testingFile])

        #Utils.plotDensity([trainingFile,testingFile])
        #Utils.plot([trainingFile,testingFile])

        if config.OC_SVM == 0: # multi-class svm
            if config.CROSS_VALIDATION == 0:
                #print 'WARNING: NB classifier with Bi-Di. ###########///////////XXXXXX???????? '
                #return wekaAPI.execute(trainingFile, testingFile, "weka.classifiers.bayes.NaiveBayes", ['-K'])

                return wekaAPI.execute( trainingFile,
                                 testingFile,
                                 "weka.Run weka.classifiers.functions.LibSVM",
                                 ['-K','2', # RBF kernel
                                  '-G','0.0000019073486328125', # Gamma
                                  ##May20 '-Z', # normalization 18 May 2015
                                  '-C','131072', # Cost
                                  #'-S','2', # one-class svm
                                  '-B'] )  # confidence

            else:
                file = Utils.joinTrainingTestingFiles(trainingFile, testingFile) # join and shuffle
                return wekaAPI.executeCrossValidation( file,
                                 "weka.Run weka.classifiers.functions.LibSVM",
                                 ['-x',str(config.CROSS_VALIDATION), # number of folds
                                  '-K','2', # RBF kernel
                                  '-G','0.0000019073486328125', # Gamma
                                  ##May20 '-Z', # normalization 18 May 2015
                                  '-C','131072', # Cost
                                  '-B'] ) # confidence
        else: # one-class svm
            if config.CROSS_VALIDATION == 0:
                print str(config.SVM_KERNEL)
                print str(config.OC_SVM_Nu)
                return wekaAPI.executeOneClassSVM( trainingFile,
                                 testingFile,
                                 "weka.Run weka.classifiers.functions.LibSVM",
                                 ['-K',str(config.SVM_KERNEL),
                                  #'-K','2', # RBF kernel
                                  #'-G','0.0000019073486328125', # Gamma
                                  ##May20 '-Z', # normalization 18 May 2015
                                  #'-C','131072', # Cost
                                  #'-N','0.001', # nu
                                  '-N',str(config.OC_SVM_Nu), # nu
                                  '-S','2'])#, # one-class svm
                                  #'-B'] )  # confidence
            else:
                file = Utils.joinTrainingTestingFiles(trainingFile, testingFile) # join and shuffle
                return wekaAPI.executeCrossValidation( file,
                                 "weka.Run weka.classifiers.functions.LibSVM",
                                 ['-x',str(config.CROSS_VALIDATION), # number of folds
                                  '-K','2', # RBF kernel
                                  '-G','0.0000019073486328125', # Gamma
                                  ##May20 '-Z', # normalization 18 May 2015
                                  '-C','131072', # Cost
                                  '-B'] ) # confidence


    '''
    #one class svm
    if config.CROSS_VALIDATION == 0:
        return wekaAPI.executeOneClassSVM( trainingFile,
                         testingFile,
                         "weka.Run weka.classifiers.functions.LibSVM",
                         ['-K','2', # RBF kernel
                          '-G','0.0000019073486328125', # Gamma
                          ##May20 '-Z', # normalization 18 May 2015
                          '-C','131072', # Cost
                          #'-N','0.2', # nu, def: 0.5
                          '-S','2'])#, # one-class svm
                          #'-B'] )  # confidence
    else:
        file = Utils.joinTrainingTestingFiles(trainingFile, testingFile) # join and shuffle
        return wekaAPI.executeCrossValidation( file,
                         "weka.Run weka.classifiers.functions.LibSVM",
                         ['-x',str(config.CROSS_VALIDATION), # number of folds
                          '-K','2', # RBF kernel
                          '-G','0.0000019073486328125', # Gamma
                          ##May20 '-Z', # normalization 18 May 2015
                          '-C','131072', # Cost
                          '-B'] ) # confidence



    @staticmethod
    def classify(runID, trainingSet, testingSet):
        print 'DT'
        [trainingFile, testingFile] = arffWriter.writeArffFiles(runID, trainingSet, testingSet)
        return wekaAPI.execute(trainingFile,
                               testingFile,
                               "weka.classifiers.trees.J48",
                               ['-C', '0.25',
                                '-M', '2'])

    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )

        if config.n_components_PCA != 0:
            [trainingFile,testingFile] = Utils.calcPCA2([trainingFile,testingFile])

        if config.n_components_LDA != 0:
            [trainingFile,testingFile] = Utils.calcLDA4([trainingFile,testingFile])

        if config.n_components_QDA != 0:
            [trainingFile,testingFile] = Utils.calcQDA([trainingFile,testingFile])

        return wekaAPI.execute( trainingFile,
                             testingFile,
                             "weka.Run weka.classifiers.functions.LibSVM",
                             [#'-K','0', # Linear kernel
                              '-K','2', # RBF kernel
                              #'-G','0.0000019073486328125', # Gamma
                              '-G','0.000030518',
                              ##May20 '-Z', # normalization 18 May 2015
                              #'-C','131072',
                              '-C','8'] ) # Cost



    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )

        if config.n_components_PCA != 0:
            [trainingFile,testingFile] = Utils.calcPCA2([trainingFile,testingFile])

        if config.n_components_LDA != 0:
            [trainingFile,testingFile] = Utils.calcLDA6([trainingFile,testingFile])

        if config.n_components_QDA != 0:
            [trainingFile,testingFile] = Utils.calcQDA([trainingFile,testingFile])

        return wekaAPI.execute( trainingFile, testingFile, "weka.classifiers.bayes.NaiveBayes", ['-K'] )

    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )
        return wekaAPI.execute( trainingFile,
                             testingFile,
                             "weka.Run weka.classifiers.functions.LibSVM",
                             ['-K','2', # RBF kernel
                              '-G','0.0000019073486328125', # Gamma
                              ##May20 '-Z', # normalization 18 May 2015
                              '-C','131072'] ) # Cost


    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )
        return wekaAPI.execute( trainingFile, testingFile, "weka.classifiers.bayes.NaiveBayes", ['-K'] )


    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )
        return wekaAPI.execute( trainingFile,
                             testingFile,
                             "weka.classifiers.trees.RandomForest",
                             ['-I','10', #
                              '-K','0', #
                              '-S','1'] ) #

    '''