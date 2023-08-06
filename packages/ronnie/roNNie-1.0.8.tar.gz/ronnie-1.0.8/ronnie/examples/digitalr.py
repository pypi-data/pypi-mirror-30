#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# Version      : dev01
# Summary      : Only 1 line of code to build the input layer from a valid form csv
#			   : Default Input Format:1st column : Label, the rest of columns : Image Pixels 
# Testing Page -> have to further revise
#############################################################################################
import os
import sys
import pandas as pd
import numpy as np
import logging

import ronnie.meta 						as meta
import ronnie.lib.util					as util

import ronnie.lib.optimizer.CNNModel   			as CNNModel
import ronnie.lib.collector.drCollector    		as collector
import ronnie.lib.monitor.logKeeper 			as lk
import ronnie.lib.monitor.plottor  	    		as plottor

############################################
#ModelDef : ModelTower and Configuration
############################################
import designer.c1p1d1			as designer
import conf.cnnCfg				as cfg

logger = logging.getLogger("digitalr")
try:
	cfg.basicCfg[meta.PROJECT_PATH] = PROJECTPATH
except:
	raise ValueError("Enter the ProjectPath at . i.e. \"C:/AIProjects/Project1\"")
	sys.exit(1)
	
lk.initial(cfg.basicCfg[meta.PROJECT_PATH], logLevel=logging.DEBUG)

def main():
	try:
		logger.debug("LOG LEVEL {0}".format(logging.DEBUG))
		
		logger.info("Start 	: Part 1 : Model Preparation")
		
		logger.info("Start	  : Part 1.1 : Declare the CNN Model Defination")
########################################################################################################
#INSTRUCTURES: 4 steps to declare the CNN Model Defination
########################################################################################################
#Step 1: Adjust conv. Layers, pool Layers, dense Layers in array structure if necessary
#Step 2: Adjust modelTower to define the relations of Layers if necessary
#Step 3: Adjust the basicCfg, TrainCfg, EvalCfg if necessary
#Step 4: The CNN Model is defined and will build while Train, Eval, Predict according to the Defination
########################################################################################################
		designer.modelDef = {    
							meta.MODEL_NAME			: "CNNModel-test28-restructure",
							meta.MODEL				: designer.modelTower,
							meta.BASIC_CONFIG		: cfg.basicCfg, 
							meta.DATA_CONFIG		: cfg.dataCfg,
							meta.TRAIN_CONFIG 		: cfg.trainCfg,
							meta.EVAL_CONFIG 		: cfg.evalCfg,
						}	
						
		
		logger.info("Finished	  : Part 1.1 : CNN Model Defination was declared.")
		
		
		logger.info("Step 1.2: Importing Data")
		dir = os.path.dirname(__file__)

		####Prepare Training Data####
		dataFileLoc = os.path.join(dir,"./data/digitalRec/train.csv")
		orgDF = collector.initial(dataFileLoc)
		logger.info("Original Data Shape {0}".format(orgDF.shape))
		
		####Prepare Training Data####
		predictFileLoc = os.path.join(dir,"./data/digitalRec/test.csv")
		predictDF = collector.initial(predictFileLoc)
		logger.info("PredictData Shape {0}".format(predictDF.shape))
		logger.info("Finished : Part 1.1 : Data was imported.")
###################################################################################
# Return Object from buildFormDF are ImgXs and LabelYs in dict Structure
# {meta.DATA_INPUTXs: imgXs, meta.DATA_LABELYs: labelYs}
###################################################################################		
		logger.info("Start	  : Step 1.3: Contructing Data to fit the model")
		trainData 		= collector.buildFromDF(orgDF,batchNum=1, batchSize=30000)
		
#		imgXs = trainData[meta.DATA_INPUTXs][0:25]
#		labelYs = trainData[meta.DATA_LABELYs][0:25]
#		#print 25 samples to study
#		logger.info("Plot Samples to study the data")
#		collector.plotImgXsSamples(imgXs,labelYs,5, 5)
		
		evalData 		= collector.buildFromDF(orgDF,batchNum=5, batchSize=10000)
		logger.info("Finished : Part 1.2 : Train,Eval Data was contructed.")
###################################################################################
#REMINDER: WithLabel = False : 
###################################################################################
#Please define the imgStartCol to the correct position
#By default while WithLabel = True, the imgStartCol position is 1
###################################################################################		
		predictData 	=collector.buildFromDF(predictDF, withLabels=False,xStartCol=0)
		
		logger.info("Finished : Part 1.4 : Predict Data was contructed.")


#################################################################################################
#						PART 2 : Modeling
#################################################################################################
#############################################################
# Initialize session variables			
#############################################################
		CNNModel.initialEnvironment()

#############################################################
#############Training########################################
#############################################################
		#does it mean, 100 steps would use 80 samples each of batch size 8000? 
		logger.info("Start : Part 2.1: Model Training.")

		logger.info("Training imgXs   Shape: {0} dType: {1} ".format(trainData[meta.DATA_INPUTXs].shape,trainData[meta.DATA_INPUTXs].dtype))
		logger.info("Training LabelYs Shape: {0} dType: {1} ".format(trainData[meta.DATA_LABELYs].shape,trainData[meta.DATA_INPUTXs].dtype))		

##############################################################################
# tranNeval use to identify the model accuracy from different dataset
#50 - cycles
#5000 - samples
#1 - steps of training
#It asked the CNNModel to execute 50 cycles, each cycles use 5000 samples with 1 taining step.
#You can turn off the evalation to speed up the training process by add ,withEval=False
#Statistic of Evaluation can find at ./models/{modelName}/evalStat/
#Statistic Chart can find at ./models/{modelName}/figures/
#To store more statistic for analysis, you could change the evalStep=1, however, the training speed is affected
##############################################################################
		logger.info("at example1: CHECK TYPE: InputX(dtype) : {0} | LabelYs(dtype):{1}".format(trainData[meta.DATA_INPUTXs].dtype, trainData[meta.DATA_LABELYs].dtype))

		eResult = CNNModel.trainNeval(trainData, evalData, designer.modelDef, 10, 5000, 1, evalSteps=1)

#############################################################
#Use the below commands if you'd like to split the training and evaluation	
#		tResult = CNNModel.trainN(trainData[meta.DATA_INPUTXs],trainData[meta.DATA_LABELYs], modelDef, samples, steps)
#		eResult = CNNModel.modelEval(evalData[meta.DATA_INPUTXs], evalData[meta.DATA_LABELYs], designer.modelDef)
#############################################################		
		
		arrEvalAcc = eResult["accuracy"]
		arrEvalSteps = eResult["global_step"]
		arrEvalLosses = eResult["loss"]
			
		logger.info("Finished : Part 2.2: eResult.{0}".format(eResult))

################################################
# Save the Evaluation Result
################################################		

		data = {"steps": arrEvalSteps,"acc" :arrEvalAcc,"loss" : arrEvalLosses}
		
################################################
# Show the Evaluation Accuracy Statistic Graph
################################################		
			
		plottor.plotModelAcc(designer.modelDef[meta.MODEL_NAME], designer.modelDef[meta.MODEL_NAME])
		logger.info("Finished : Part 2.3: Plotting Statistic")			
		
#############################################################		
#############Prediction######################################
#############################################################		

		logger.info("Start : Part 2.4: Model Prediction.")

		logger.info("Predict imgXs   Shape: {0} ".format(predictData[meta.DATA_INPUTXs].shape))
		logger.info("Predict LabelYs Shape: {0} ".format(predictData[meta.DATA_LABELYs].shape))
           
		pResult = CNNModel.modelPredict(predictData[meta.DATA_INPUTXs], predictData[meta.DATA_LABELYs], designer.modelDef)
		
		logger.info("Finished : Part 2.4: Prediction.{0}".format(pResult))
			
###############################################################
#############Export Sample Result##############################
###############################################################
# The Prediction result stored at ./models/{modelName}/export/
# or you can use CNNModel.predictExport(pResults, modelDef) to export the file seperately.
################################################################
		logger.info("Finished. PREDICTION data exported.")

		logger.info("Enjoy! Email us your comments and credits. Thanks.")
			
	except SystemExit:  
		 pass  	
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
		#sys.exit(1)	
if __name__ == "__main__":
 # if you call this script from the command line (the shell) it will
 # run the 'main' function
	main()	