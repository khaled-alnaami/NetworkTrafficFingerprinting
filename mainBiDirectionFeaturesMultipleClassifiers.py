# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.
# Extended by Khaled M. Alnaami

import sys
import config
import time
import os
import random
import getopt
import string
import itertools
import shutil # to remove folders

# custom
from Datastore import Datastore
from Webpage import Webpage

# countermeasures
from PadToMTU import PadToMTU
from PadRFCFixed import PadRFCFixed
from PadRFCRand import PadRFCRand
from PadRand import PadRand
from PadRoundExponential import PadRoundExponential
from PadRoundLinear import PadRoundLinear
from MiceElephants import MiceElephants
from DirectTargetSampling import DirectTargetSampling
from Folklore import Folklore
from WrightStyleMorphing import WrightStyleMorphing

# classifiers
from LiberatoreClassifier import LiberatoreClassifier
from WrightClassifier import WrightClassifier
from BandwidthClassifier import BandwidthClassifier
from HerrmannClassifier import HerrmannClassifier
from TimeClassifier import TimeClassifier
from PanchenkoClassifier import PanchenkoClassifier
from VNGPlusPlusClassifier import VNGPlusPlusClassifier
from VNGClassifier import VNGClassifier
from JaccardClassifier import JaccardClassifier
from ESORICSClassifier import ESORICSClassifier
from AdversialClassifier import AdversialClassifier
from AdversarialClassifierOnPanchenko import AdversarialClassifierOnPanchenko
from AdversarialClassifierBiDirectionFeaturesOnly import AdversarialClassifierBiDirectionFeaturesOnly
#from AdversialClassifierTor import AdversialClassifierTor
#from AdversialClassifierBloomFilter import AdversialClassifierBloomFilter
#from AdversarialClassifierOnPanchenkoBloomFilter import AdversarialClassifierOnPanchenkoBloomFilter
from ToWangFilesClosedWorld import ToWangFilesClosedWorld

def intToCountermeasure(n):
    countermeasure = None
    if n == config.PAD_TO_MTU:
        countermeasure = PadToMTU
    elif n == config.RFC_COMPLIANT_FIXED_PAD:
        countermeasure = PadRFCFixed
    elif n == config.RFC_COMPLIANT_RANDOM_PAD:
        countermeasure = PadRFCRand
    elif n == config.RANDOM_PAD:
        countermeasure = PadRand
    elif n == config.PAD_ROUND_EXPONENTIAL:
        countermeasure = PadRoundExponential
    elif n == config.PAD_ROUND_LINEAR:
        countermeasure = PadRoundLinear
    elif n == config.MICE_ELEPHANTS:
        countermeasure = MiceElephants
    elif n == config.DIRECT_TARGET_SAMPLING:
        countermeasure = DirectTargetSampling
    elif n == config.WRIGHT_STYLE_MORPHING:
        countermeasure = WrightStyleMorphing
    elif n > 10:
        countermeasure = Folklore

        # FIXED_PACKET_LEN: 1000,1250,1500
        if n in [11,12,13,14]:
            Folklore.FIXED_PACKET_LEN    = 1000
        elif n in [15,16,17,18]:
            Folklore.FIXED_PACKET_LEN    = 1250
        elif n in [19,20,21,22]:
            Folklore.FIXED_PACKET_LEN    = 1500

        if n in [11,12,13,17,18,19]:
            Folklore.TIMER_CLOCK_SPEED   = 20
        elif n in [14,15,16,20,21,22]:
            Folklore.TIMER_CLOCK_SPEED   = 40

        if n in [11,14,17,20]:
            Folklore.MILLISECONDS_TO_RUN = 0
        elif n in [12,15,18,21]:
            Folklore.MILLISECONDS_TO_RUN = 5000
        elif n in [13,16,19,22]:
            Folklore.MILLISECONDS_TO_RUN = 10000

        if n==23:
            Folklore.MILLISECONDS_TO_RUN = 0
            Folklore.FIXED_PACKET_LEN    = 1250
            Folklore.TIMER_CLOCK_SPEED   = 40
        elif n==24:
            Folklore.MILLISECONDS_TO_RUN = 0
            Folklore.FIXED_PACKET_LEN    = 1500
            Folklore.TIMER_CLOCK_SPEED   = 20
        elif n==25:
            Folklore.MILLISECONDS_TO_RUN = 5000
            Folklore.FIXED_PACKET_LEN    = 1000
            Folklore.TIMER_CLOCK_SPEED   = 40
        elif n==26:
            Folklore.MILLISECONDS_TO_RUN = 5000
            Folklore.FIXED_PACKET_LEN    = 1500
            Folklore.TIMER_CLOCK_SPEED   = 20
        elif n==27:
            Folklore.MILLISECONDS_TO_RUN = 10000
            Folklore.FIXED_PACKET_LEN    = 1000
            Folklore.TIMER_CLOCK_SPEED   = 40
        elif n==28:
            Folklore.MILLISECONDS_TO_RUN = 10000
            Folklore.FIXED_PACKET_LEN    = 1250
            Folklore.TIMER_CLOCK_SPEED   = 20


    return countermeasure

def intToClassifier(n):
    classifier = None
    if n == config.LIBERATORE_CLASSIFIER:
        classifier = LiberatoreClassifier
    elif n == config.WRIGHT_CLASSIFIER:
        classifier = WrightClassifier
    elif n == config.BANDWIDTH_CLASSIFIER:
        classifier = BandwidthClassifier
    elif n == config.HERRMANN_CLASSIFIER:
        classifier = HerrmannClassifier
    elif n == config.TIME_CLASSIFIER:
        classifier = TimeClassifier
    elif n == config.PANCHENKO_CLASSIFIER:
        classifier = PanchenkoClassifier
    elif n == config.VNG_PLUS_PLUS_CLASSIFIER:
        classifier = VNGPlusPlusClassifier
    elif n == config.VNG_CLASSIFIER:
        classifier = VNGClassifier
    elif n == config.JACCARD_CLASSIFIER:
        classifier = JaccardClassifier
    elif n == config.ESORICS_CLASSIFIER:
        classifier = ESORICSClassifier
    elif n == config.ADVERSIAL_CLASSIFIER:
        classifier = AdversialClassifier
    elif n == config.ADVERSARIAL_CLASSIFIER_ON_PANCHENKO:
        classifier = AdversarialClassifierOnPanchenko
    elif n == config.ADVERSARIAL_CLASSIFIER_BiDirection_Only:
        classifier = AdversarialClassifierBiDirectionFeaturesOnly
    elif n == config.TO_WANG_FILES_CLOSED_WORLD:
        classifier = ToWangFilesClosedWorld
    '''
    elif n == config.ADVERSIAL_CLASSIFIER_TOR:
        classifier = AdversialClassifierTor
    elif n == config.ADVERSIAL_CLASSIFIER_BLOOM_FILTER:
        classifier = AdversialClassifierBloomFilter
    elif n == config.ADVERSARIAL_CLASSIFIER_ON_PANCHENKO_BLOOM_FILTER:
        classifier = AdversarialClassifierOnPanchenkoBloomFilter
    '''

    return classifier

def usage():
    print """
    -N [int] : use [int] websites from the dataset
               from which we will use to sample a privacy
               set k in each experiment (default 775)

    -k [int] : the size of the privacy set (default 2)

    -d [int]: dataset to use
        0: Liberatore and Levine Dataset (OpenSSH)
        1: Herrmann et al. Dataset (OpenSSH)
        2: Herrmann et al. Dataset (Tor)
        3: Android Tor dataset
        (default 1)

    -C [int] : classifier to run, if multiple classifiers, then separate by a comma (example: -C 23,3,15)
        0: Liberatore Classifer
        1: Wright et al. Classifier
        2: Jaccard Classifier
        3: Panchenko et al. Classifier
        5: Lu et al. Edit Distance Classifier
        6: Herrmann et al. Classifier
        4: Dyer et al. Bandwidth (BW) Classifier
        10: Dyer et al. Time Classifier
        14: Dyer et al. Variable n-gram (VNG) Classifier
        15: Dyer et al. VNG++ Classifier
        21: Adversarial Classifier
        22: Adversarial Classifier On Panchenko
        31: Adversarial Classifier Tor
        41: Adversarial Classifier using Bloom Filter
        42: Adversarial Classifier On Panchenko using Bloom Filter
        23: Adversarial Classifier Using BiDirection features only (no panch features)
        101: To Wang Files - Closed World Classifier. Should be with option -x 1."
        (default 0)

    -c [int]: countermeasure to use
        0: None
        1: Pad to MTU
        2: Session Random 255
        3: Packet Random 255
        4: Pad Random MTU
        5: Exponential Pad
        6: Linear Pad
        7: Mice-Elephants Pad
        8: Direct Target Sampling
        9: Traffic Morphing
        (default 0)

    -t [int]: number of trials to run per experiment (default 1)

    -t [int]: number of training traces to use per experiment (default 16)

    -T [int]: number of testing traces to use per experiment (default 4)

    -D [0 or 1]: Packet Size as a word (default 0)
    -E [0 or 1]: UniBurst Size as a word (default 0)
    -F [0 or 1]: UniBurst Time as a word (default 0)
    -G [0 or 1]: UniBurst Number as a word (default 0)
    -H [0 or 1]: BiBurst Size as a word (default 0)
    -I [0 or 1]: BiBurst Time as a word (default 0)

    -A [0 or 1]: Ignore ACK packets (default 0, ACK packets NOT ignored (ACK included)

    -V [0 or 1]: Five number summary, for the Adversarial Classifier (Default is 0)

    -m : Number of Monitored Websites for Open World (m < k). (default -1: Not An Open World Scenario)

    -x [0 or 1]: 0: no Extra,   1: Extra.    (default 0)   with -C 101: To Wang Files - Closed World Classifier (for generating OSAD files)

    -P : Number of Principal Component Analysis (PCA) components (default 0: No PCA required.) It has to be <= number of sum of instances in both training and testing files

    -g : Linear Discriminant Analysis. Number of Principal Components (default 0: No LDA required.) It has to be < number of classes. g for generalized eigenvalue problem

    -b: bucket size (default: 600)

    -l: lasso (default: 0, no lasso)

    """

def run():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:T:N:k:c:C:d:n:r:B:D:E:F:G:H:I:J:K:L:M:A:m:V:P:g:q:x:b:l:h")
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    char_set = string.ascii_lowercase + string.digits
    runID = ''.join(random.sample(char_set,8))

    webpageIndex = 1; # Global variable to write the Wang OSAD file names. For Wang OSAD files numbering X-Y.txt (Closed World) // -C 101.  Oct 14, 2015

    for o, a in opts:
        if o in ("-k"):
            config.BUCKET_SIZE = int(a)
        elif o in ("-C"):
            config.CLASSIFIER_LIST = a.split(",")
        elif o in ("-d"):
            config.DATA_SOURCE = int(a)
        elif o in ("-c"):
            config.COUNTERMEASURE = int(a)
        elif o in ("-N"):
            config.TOP_N = int(a)
        elif o in ("-t"):
            config.NUM_TRAINING_TRACES = int(a)
        elif o in ("-T"):
            config.NUM_TESTING_TRACES = int(a)
        elif o in ("-n"):
            config.NUM_TRIALS = int(a)
        elif o in ("-r"):
            runID = str(a)
        elif o in ("-D"):
            if int(a) == 1:
                config.GLOVE_OPTIONS['packetSize'] = 1
        elif o in ("-E"):
            if int(a) == 1:
                config.GLOVE_OPTIONS['burstSize'] = 1
        elif o in ("-F"):
            if int(a) == 1:
                config.GLOVE_OPTIONS['burstTime'] = 1
        elif o in ("-G"):
            if int(a) == 1:
                config.GLOVE_OPTIONS['burstNumber'] = 1
        elif o in ("-H"):
            if int(a) == 1:
                config.GLOVE_OPTIONS['biBurstSize'] = 1
        elif o in ("-I"):
            if int(a) == 1:
                config.GLOVE_OPTIONS['biBurstTime'] = 1
        elif o in ("-B"):
            config.GLOVE_OPTIONS['ModelTraceNum'] = int(a)
        elif o in ("-J"):
            config.GLOVE_PARAMETERS['window'] = int(a)
        elif o in ("-K"):
            config.GLOVE_PARAMETERS['no_components'] = int(a)
        elif o in ("-L"):
            config.GLOVE_PARAMETERS['learning_rate'] = float(a)
        elif o in ("-M"):
            config.GLOVE_PARAMETERS['epochs'] = int(a)
        elif o in ("-A"):
            config.IGNORE_ACK = bool(int(a))
        elif o in ("-m"):
            config.NUM_MONITORED_SITES = int(a)
        elif o in ("-V"):
            config.FIVE_NUM_SUM = int(a)
        elif o in ("-x"):
            config.EXTRA = int(a)
        elif o in ("-P"):
            config.n_components_PCA = int(a)
        elif o in ("-g"):
            config.n_components_LDA = int(a)
        elif o in ("-q"):
            config.n_components_QDA = int(a)
        elif o in ("-b"):
            config.bucket_Size = int(a)
        elif o in ("-l"):
            config.lasso = float(a) # Float for threshold
        else:
            usage()
            sys.exit(2)

    config.RUN_ID = runID

    if not os.path.exists(config.OUTPUT_DIR):
        os.mkdir(config.OUTPUT_DIR)

    if not os.path.exists(config.WANG):
        os.mkdir(config.WANG)

    if not os.path.exists(config.CACHE_DIR):
        os.mkdir(config.CACHE_DIR)

#    outputFilenameArray = ['results',
#                           'k'+str(config.BUCKET_SIZE),
#                           'c'+str(config.COUNTERMEASURE),
#                           'd'+str(config.DATA_SOURCE),
#                           'C'+str(config.CLASSIFIER),
#                           'N'+str(config.TOP_N),
#                           't'+str(config.NUM_TRAINING_TRACES),
#                           'T'+str(config.NUM_TESTING_TRACES),
#                           'D' + str(config.GLOVE_OPTIONS['packetSize']),
#                           'E' + str(config.GLOVE_OPTIONS['burstSize']),
#                           'F' + str(config.GLOVE_OPTIONS['burstTime']),
#                           'G' + str(config.GLOVE_OPTIONS['burstNumber']),
#                           'H' + str(config.GLOVE_OPTIONS['biBurstSize']),
#                           'I' + str(config.GLOVE_OPTIONS['biBurstTime']),
#                           'A' + str(int(config.IGNORE_ACK)),
#                           'V' + str(int(config.FIVE_NUM_SUM)),
#                           'P' + str(int(config.n_components_PCA)),
#                           'g' + str(int(config.n_components_LDA)),
#                           'l' + str(int(config.lasso)),
#                           'b' + str(int(config.bucket_Size))
#
#                          ]
#    outputFilename = os.path.join(config.OUTPUT_DIR,'.'.join(outputFilenameArray))
#
#    if not os.path.exists(config.CACHE_DIR):
#        os.mkdir(config.CACHE_DIR)
#
#    if not os.path.exists(outputFilename+'.output'):
#        banner = ['accuracy','overhead','timeElapsedTotal','timeElapsedClassifier']
#        f = open( outputFilename+'.output', 'w' )
#        f.write(','.join(banner))
#        f.close()
#    if not os.path.exists(outputFilename+'.debug'):
#        f = open( outputFilename+'.debug', 'w' )
#        f.close()

#    # OSAD closed world
#    tempRunID = runID
#    outputFilenameArrayOSAD = ['OSAD',
#                               tempRunID,
#                           'k'+str(config.BUCKET_SIZE),
#                           'c'+str(config.COUNTERMEASURE),
#                           'd'+str(config.DATA_SOURCE),
#                           'C'+str(config.CLASSIFIER),
#                           'N'+str(config.TOP_N),
#                           't'+str(config.NUM_TRAINING_TRACES),
#                           'T'+str(config.NUM_TESTING_TRACES)
#                          ]
#    OSADfolder = os.path.join(config.WANG,'.'.join(outputFilenameArrayOSAD))
#
#    if config.CLASSIFIER == config.TO_WANG_FILES_CLOSED_WORLD:
#            if not os.path.exists(OSADfolder):
#                os.mkdir(OSADfolder)
#            else:
#                shutil.rmtree(OSADfolder) # delete and remake folder
#                os.mkdir(OSADfolder)

    if config.DATA_SOURCE == 0:
        startIndex = config.NUM_TRAINING_TRACES
        endIndex   = len(config.DATA_SET)-config.NUM_TESTING_TRACES
    elif config.DATA_SOURCE == 1:
        maxTracesPerWebsiteH = 160
        startIndex = config.NUM_TRAINING_TRACES
        endIndex   = maxTracesPerWebsiteH-config.NUM_TESTING_TRACES
    elif config.DATA_SOURCE == 2:
        maxTracesPerWebsiteH = 18
        #29May2015 maxTracesPerWebsiteH = 160 # Changed from 18 to 160 on 28May2015
        startIndex = config.NUM_TRAINING_TRACES
        endIndex   = maxTracesPerWebsiteH-config.NUM_TESTING_TRACES
    elif config.DATA_SOURCE == 3:
        config.DATA_SET = config.DATA_SET_ANDROID_TOR
        startIndex = config.NUM_TRAINING_TRACES
        endIndex   = len(config.DATA_SET)-config.NUM_TESTING_TRACES
        config.PCAP_ROOT = os.path.join(config.BASE_DIR   ,'pcap-logs-Android-Tor-Grouping')

    for i in range(config.NUM_TRIALS):

        #startStart = time.time()

        webpageIds = range(0, config.TOP_N - 1)
        random.shuffle( webpageIds )
        webpageIds = webpageIds[0:config.BUCKET_SIZE]

        seed = random.randint( startIndex, endIndex )

        #preCountermeasureOverhead = 0
        #postCountermeasureOverhead = 0
#
        ##classifier     = intToClassifier(config.CLASSIFIER)
        #countermeasure = intToCountermeasure(config.COUNTERMEASURE)
#
        #trainingSet = []
        #testingSet  = []
#
        #targetWebpage = None
        #extraCtr = 0
###
        #assign config.CLASSIFIER here
        #loop over each classifier
        for clsfr in config.CLASSIFIER_LIST:
            preCountermeasureOverhead = 0
            postCountermeasureOverhead = 0

            #classifier     = intToClassifier(config.CLASSIFIER)
            countermeasure = intToCountermeasure(config.COUNTERMEASURE)

            trainingSet = []
            testingSet  = []

            targetWebpage = None
            extraCtr = 0
            startStart = time.time()


            #if int(clsfr) == 23: # Bi-Di
            #    config.IGNORE_ACK = False

            config.CLASSIFIER = int(clsfr)
            classifier     = intToClassifier(config.CLASSIFIER)


            outputFilenameArray = ['results',
                                   'k'+str(config.BUCKET_SIZE),
                                   'c'+str(config.COUNTERMEASURE),
                                   'd'+str(config.DATA_SOURCE),
                                   'C'+str(config.CLASSIFIER),
                                   'N'+str(config.TOP_N),
                                   't'+str(config.NUM_TRAINING_TRACES),
                                   'T'+str(config.NUM_TESTING_TRACES),
                                   'D' + str(config.GLOVE_OPTIONS['packetSize']),
                                   'E' + str(config.GLOVE_OPTIONS['burstSize']),
                                   'F' + str(config.GLOVE_OPTIONS['burstTime']),
                                   'G' + str(config.GLOVE_OPTIONS['burstNumber']),
                                   'H' + str(config.GLOVE_OPTIONS['biBurstSize']),
                                   'I' + str(config.GLOVE_OPTIONS['biBurstTime']),
                                   'A' + str(int(config.IGNORE_ACK)),
                                   'V' + str(int(config.FIVE_NUM_SUM)),
                                   'P' + str(int(config.n_components_PCA)),
                                   'g' + str(int(config.n_components_LDA)),
                                   'l' + str(int(config.lasso)),
                                   'b' + str(int(config.bucket_Size))

                                  ]
            outputFilename = os.path.join(config.OUTPUT_DIR,'.'.join(outputFilenameArray))

            if not os.path.exists(config.CACHE_DIR):
                os.mkdir(config.CACHE_DIR)

            if not os.path.exists(outputFilename+'.output'):
                banner = ['accuracy','overhead','timeElapsedTotal','timeElapsedClassifier']
                f = open( outputFilename+'.output', 'w' )
                f.write(','.join(banner))
                f.close()
            if not os.path.exists(outputFilename+'.debug'):
                f = open( outputFilename+'.debug', 'w' )
                f.close()

            # OSAD closed world
            tempRunID = runID
            outputFilenameArrayOSAD = ['OSAD',
                                       tempRunID,
                                   'k'+str(config.BUCKET_SIZE),
                                   'c'+str(config.COUNTERMEASURE),
                                   'd'+str(config.DATA_SOURCE),
                                   'C'+str(config.CLASSIFIER),
                                   'N'+str(config.TOP_N),
                                   't'+str(config.NUM_TRAINING_TRACES),
                                   'T'+str(config.NUM_TESTING_TRACES)
                                  ]
            OSADfolder = os.path.join(config.WANG,'.'.join(outputFilenameArrayOSAD))

            if config.CLASSIFIER == config.TO_WANG_FILES_CLOSED_WORLD:
                    if not os.path.exists(OSADfolder):
                        os.mkdir(OSADfolder)
                    else:
                        shutil.rmtree(OSADfolder) # delete and remake folder
                        os.mkdir(OSADfolder)

            for webpageId in webpageIds:
                if config.DATA_SOURCE == 0 or config.DATA_SOURCE == 3:
                    webpageTrain = Datastore.getWebpagesLL( [webpageId], seed-config.NUM_TRAINING_TRACES, seed )
                    webpageTest  = Datastore.getWebpagesLL( [webpageId], seed, seed+config.NUM_TESTING_TRACES )
                elif config.DATA_SOURCE == 1 or config.DATA_SOURCE == 2:
                    webpageTrain = Datastore.getWebpagesHerrmann( [webpageId], seed-config.NUM_TRAINING_TRACES, seed )
                    webpageTest  = Datastore.getWebpagesHerrmann( [webpageId], seed, seed+config.NUM_TESTING_TRACES )

                webpageTrain = webpageTrain[0]
                webpageTest = webpageTest[0]

                if targetWebpage == None:
                    targetWebpage = webpageTrain

                preCountermeasureOverhead  += webpageTrain.getBandwidth()
                preCountermeasureOverhead  += webpageTest.getBandwidth()

                metadata = None
                if config.COUNTERMEASURE in [config.DIRECT_TARGET_SAMPLING, config.WRIGHT_STYLE_MORPHING]:
                    metadata = countermeasure.buildMetadata( webpageTrain,  targetWebpage )


                i = 0
                for w in [webpageTrain, webpageTest]:
                    for trace in w.getTraces():
                        if countermeasure:
                            if config.COUNTERMEASURE in [config.DIRECT_TARGET_SAMPLING, config.WRIGHT_STYLE_MORPHING]:
                                if w.getId()!=targetWebpage.getId():
                                    traceWithCountermeasure = countermeasure.applyCountermeasure( trace,  metadata )
                                else:
                                    traceWithCountermeasure = trace
                            else:
                                traceWithCountermeasure = countermeasure.applyCountermeasure( trace )
                        else:
                            traceWithCountermeasure = trace

                        postCountermeasureOverhead += traceWithCountermeasure.getBandwidth()


                        if config.EXTRA == 0: # Normal classifiers
                            instance = classifier.traceToInstance( traceWithCountermeasure )

                            if instance:
                                if i==0:
                                    trainingSet.append( instance )
                                elif i==1:
                                    testingSet.append( instance )
                        else: # OSAD classifier (just to write Wang closed world files
                            extraCtr += 1
                            instances = classifier.traceToInstances( traceWithCountermeasure, webpageIndex, extraCtr, OSADfolder )
                            #no need for the following if we want to generate OSAD files only
                            #in future in sha Allah, if setwise needed, then uncomment the following lines as we need the arff files
                            #if instances:
                            #    if i==0:
                            #        for instance in instances:
                            #            trainingSet.append( instance )
                            #    elif i==1:
                            #        for instance in instances:
                            #            testingSet.append( instance )


                        #instance = classifier.traceToInstance( traceWithCountermeasure )

                        #if instance:
                        #    if i==0:
                        #        trainingSet.append( instance )
                        #    elif i==1:
                        #        testingSet.append( instance )

                    i+=1
                if config.CLASSIFIER == config.TO_WANG_FILES_CLOSED_WORLD:
                    webpageIndex += 1 # OSAD or Open World KNN files
                    extraCtr = 0
            ###################

            startClass = time.time()

            #[accuracy,debugInfo] = classifier.classify( runID, trainingSet, testingSet )

            if config.CLASSIFIER == config.TO_WANG_FILES_CLOSED_WORLD:
                [accuracy,debugInfo] = ['NA', []]
            else:
                [accuracy,debugInfo] = classifier.classify( runID, trainingSet, testingSet )

            end = time.time()

            overhead = str(postCountermeasureOverhead)+'/'+str(preCountermeasureOverhead)

            output = [accuracy,overhead]

            output.append( '%.2f' % (end-startStart) )
            output.append( '%.2f' % (end-startClass) )

            summary = ', '.join(itertools.imap(str, output))

            f = open( outputFilename+'.output', 'a' )
            f.write( "\n"+summary )
            f.close()

            f = open( outputFilename+'.debug', 'a' )
            for entry in debugInfo:
                f.write( entry[0]+','+entry[1]+"\n" )
            f.close()

if __name__ == '__main__':
    run()
