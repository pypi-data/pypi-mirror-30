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
import sys
import pandas as pd
import logging
import numpy as np
import matplotlib.pyplot as plt

import 	ronnie.meta 					as meta
import 	ronnie.lib.util 				as util

logger = logging.getLogger("roNNie")

@util.timer
def initial(dataFileLoc):
	try:
		logger.info("......READing......")
		dataFile = pd.read_csv(dataFileLoc)	
	except IOError as ioE:
		logger.error("Cannot open File %s"% (dataFileLoc))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise		
	return dataFile

		

def plotImgXsSamples(imgXs,labelYs=None,cols=5, rows=5):	
	imgSize = imgXs.shape[1]
	if not labelYs is None:
		hasLabelYs="with Labels" 	
	
	if imgSize > 0:
		fig=plt.figure(figsize=(imgSize, imgSize))
		fig.suptitle(str(cols*rows) + " Digit Samples " + hasLabelYs)
		fig.subplots_adjust(wspace=1, hspace=1)
		for i in range(0, imgXs.shape[0]):
			img = imgXs[i]
			img = img.reshape((imgSize, imgSize))
			sp = fig.add_subplot(rows, cols, i+1)
			if not hasLabelYs == "":
				anno = "Label " + str(labelYs[i])
				sp.set_title(anno,fontsize=12)
			plt.imshow(img)
			
		return plt.show()
	return None
	
#input  (Default): dataframe of File, withLabel at the begining of each row
#output (Default): all rows of reshaped imgXs and labelYs at column 0
#output sample : imgXs, labelYs = extractDataFromFile(xxxxx)	
@util.timer
def buildFromDF(df, withLabels=True, labelCol=0, xNeedReshape=True, xStartCol=1,imgLen=-1, batchNum=1, batchSize=-1):
	try:
		logger.info("......TRANSFORMing......")
		if batchSize == -1:
			batchSize = df.shape[0]
		if batchNum == 1:
			begin = 0
		else:
			begin = (batchNum-1) * batchSize
		end = begin + batchSize
		
		rowLen = df.shape[1]
		imgLen = rowLen
		
		if withLabels:
			labelYs = df.iloc[begin:end,labelCol:labelCol+1].values
			labelYs.astype(np.int32)
			imgLen -= 1
		else:
			labelYs = np.zeros((df.shape[0], 1), dtype=np.int32)

		#logger.info("ImgLen is {0}".format(imgLen))
		logger.info("!!LabelYs shape {0}".format(labelYs.shape ))
		inputXs = df.iloc[begin:end,xStartCol:xStartCol+imgLen+1]
		inputXs.astype(np.float32)
		
		if xNeedReshape:
			#print(imgLen)
			isImgInValidSize, imgWidthHeight = util.isSqr(imgLen)
			#print ("imgWidthHeight {0}".format(imgWidthHeight))
				
			if not isImgInValidSize:
				logger.error("!!!ERROR : IMAGE RESHAPE ERROR!!!")
				logger.error("!!!    WRONG image size {0}   !!!".format(imgLen))
				sys.exit(1)
				
				
			inputXs = inputXs.values.reshape(inputXs.shape[0],imgWidthHeight,imgWidthHeight,1)
		
		inputXs = inputXs*0.1
		inputXs32 = np.array(inputXs, dtype=np.float32)
		logger.info("Collector : Double Check inputXs type after casting 32 {0}.".format(inputXs32.dtype))
		
		labelYs32 = np.array(labelYs, dtype=np.int32)
		logger.info("Collector : Double Check labelYs type after casting 32 {0}.".format(labelYs32.dtype))
		
		output = {meta.DATA_INPUTXs: inputXs32, meta.DATA_LABELYs: labelYs32}
		
		logger.info("Collector : {0} Type {1} and {2} Type {3}.".format(meta.DATA_INPUTXs, output[meta.DATA_INPUTXs].dtype,meta.DATA_LABELYs, output[meta.DATA_LABELYs].dtype))
		logger.info("Collector : {0} Shape {1} and {2} Shape {3}.".format(meta.DATA_INPUTXs, output[meta.DATA_INPUTXs].shape,meta.DATA_LABELYs, output[meta.DATA_LABELYs].shape))
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
#-1,28,28,1
#-1(number of samples), [img?], [channel]
#-1, [xxxxx],[channel]
def main():
	return
if __name__ == "__main__":
 # if you call this script from the command line (the shell) it will
 # run the 'main' function
	main()	