#############################################################################################
#Project roNNie
#Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# Version      : dev01
# Summary      : To handle and digest the input from File to specified structure for CNNModel 
#			   : Transform *multi*,*auto detected sizes* images from csv by 1 line of code
# Description  : Default Input Format:1st column : Label, the rest of columns : Image Pixels 
#############################################################################################
import os
import sys
import pandas as pd
import logging
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as plimg

import 	ronnie.meta 					as meta
import 	ronnie.lib.util 				as util

import 	ronnie.lib.monitor.logKeeper	as lk

import pickle

logger = logging.getLogger("roNNie")

@util.timer
def initial(dataFileLoc):
	try:
		dataDict = None
		
		logger.info("......READing......")
		#dataFile = pd.read_csv(dataFileLoc)
		normalizedPath = os.path.realpath(dataFileLoc)
		
		logger.info("OS REALPATH {0}".format(normalizedPath))
		
		with open(normalizedPath, 'rb') as df:
			dataDict = pickle.load(df, encoding='bytes')
		logger.info("READ BYTES file from pickle")
	except IOError as ioE:
		logger.error("Cannot open File %s"% (dataFileLoc))
	except:
		logger.error("INITIAL - Unexpected error: {}".format(sys.exc_info()[0]))
		raise		
	return dataDict

		

def plotImgXsSamplesWithChannels(imgXs,labelYs=None,cols=5, rows=5):	
	imgSize = imgXs.shape[1]
	if not labelYs is None:
		hasLabelYs="with Labels" 	
		
	logger.info("img arr: {0}".format(imgXs[7]))
	plt.imshow(imgXs[7])
	plt.show()
	sys.exit(1)
		
	if imgSize > 0:
		fig=plt.figure(figsize=(32, 32))
		fig.suptitle(str(cols*rows) + " Digit Samples " + hasLabelYs)
		fig.subplots_adjust(wspace=1, hspace=1)
		
#		for i in range(0, imgXs.shape[0]):
		for i in range(0, 1):
			img = imgXs[10]	
			img.astype(int)
			logger.info("img Shape strange : {0}".format(img.shape))
			
			logger.info("CONVERTED FROM FLOAT TO INT : {0}".format(img))
			imgR = img[:,:,0]
			imgG = img[:,:,1]
			imgB = img[:,:,2]
#			logger.info("IMG R {0}".format(imgR))
#			logger.info("IMG G {0}".format(imgG))
#			logger.info("IMG B {0}".format(imgB))
			
			#img = img.reshape((imgSize, imgSize))
			logger.info("INDEX : {0} | IMG SHAPE {1}".format(i,img.shape))
			sp = fig.add_subplot(rows, cols, i+1)
			if not hasLabelYs == "":
				anno = "Label " + str(labelYs[i])
				sp.set_title(anno,fontsize=12)
			
			
			#plt.imshow(img,interpolation='nearest')
			sp = fig.add_subplot(rows, cols, 1)
			logger.info("IMG R array {0}".format(imgR))
			plt.imshow(imgR)
			sp = fig.add_subplot(rows, cols, 2)
			logger.info("IMG G array {0}".format(imgG))
			plt.imshow(imgG)
			sp = fig.add_subplot(rows, cols, 3)
			logger.info("IMG B array {0}".format(imgB))
			plt.imshow(imgB)
			sp = fig.add_subplot(rows, cols, 4)
			logger.info("IMG RGB array {0}".format(img))
			plt.imshow(img,interpolation='nearest')
		
		return plt.show()
	return None
	
#input  (Default): dataframe of File, withLabel at the begining of each row
#output (Default): all rows of reshaped imgXs and labelYs at column 0
#output sample : imgXs, labelYs = extractDataFromFile(xxxxx)	
@util.timer
def buildFromDF(df, withLabels=True, labelCol=0, xNeedReshape=True, xStartCol=1,imgLen=-1, batchNum=1, batchSize=-1,sysBytes=64):
	try:
		logger.info("......TRANSFORMing......")
#		logger.info(df)
		tInputXs = np.array(df[b'data'])
		logger.info("Original Data Shape {0}".format(tInputXs.shape))
		t2InputXs = tInputXs.reshape(-1,3,1024)
		logger.info("Original Data Shape {0}".format(tInputXs.shape))
		t3InputXs = t2InputXs.reshape(-1,3,32,32)
		R = t3InputXs[-1][0]
		G = t3InputXs[-1][1]
		B = t3InputXs[-1][2]
		
##		#Swap R and G
##		t3InputXs[-1][0] = B
##		t3InputXs[-1][1] = R
##		t3InputXs[-1][2] = G
		logger.info("reStrRBG {0}".format(t3InputXs.shape))

		
		logger.info("After reShape {0}".format(tInputXs.shape))
	    # Converted to right order 4-dimensions.
		inputXs = t3InputXs.transpose(0, 2, 3, 1).astype("uint8")
		logger.info("After Transpose {0}".format(inputXs.shape))
		
		labelYs = np.array(df[b'labels'])
		logger.info("LabelYs Shape {0}".format(labelYs.shape))
		
		inputXs = inputXs*0.1
		
		if	sysBytes == 32 :
			inputXs.astype(np.float32)
			labelYs.astype(np.int32)
		elif sysBytes == 64 :
			inputXs.astype(np.float64)
			labelYs.astype(np.int64)			
		else:
			raise ValueError("Wrong Bytes {0}".format(bytes))
			
		output = {meta.DATA_INPUTXs: inputXs, meta.DATA_LABELYs: labelYs}
		
		logger.debug("{0} Type {1} and {2} Type {3}.".format(meta.DATA_INPUTXs, output[meta.DATA_INPUTXs].dtype,meta.DATA_LABELYs, output[meta.DATA_LABELYs].dtype))
		logger.debug("{0} Shape {1} and {2} Shape {3}.".format(meta.DATA_INPUTXs, output[meta.DATA_INPUTXs].shape,meta.DATA_LABELYs, output[meta.DATA_LABELYs].shape))
		return output
		
	except IOError as ioE:
		logger.error("I/O error({0})".format(ioE))
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except SystemExit:  
		pass  
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
def main():
	return
if __name__ == "__main__":
 # if you call this script from the command line (the shell) it will
 # run the 'main' function
	main()	