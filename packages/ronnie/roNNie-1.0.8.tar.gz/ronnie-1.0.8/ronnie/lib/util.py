#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# Version      : dev01
# Summary      : Utililties for roNNie  
#############################################################################################
import math
import logging
import time
import datetime
import sys
import os


logger = logging.getLogger("roNNie")

def ensurePath(modelPath):
	if not os.path.exists(modelPath):
		os.makedirs(modelPath)

def getPath(part, modelName=None):
	file = None
	path = None
	if part == "exportPredict":
		path = "./models/" + modelName + "./export/"
		file = "./predict.csv"
	elif part == "stat":
		path = "./models/" + modelName + "./evalStat/"
		file = "./model.stat"
	elif part == "figures":
		path = "./models/" + modelName + "./figures/"
		datetimeStr = time.strftime("%Y%m%d%H%M%S")
		file = "./" + datetimeStr + ".png"
	elif part == "models":
		path = "./models/"
	elif part == "data":
		path = "./data/"
	elif part == "tensorlogs":
		path = "./logs/tensorflow.log"
	
	ensurePath(path)
	
	if not file is None:
		path = path + file
	
	return os.path.realpath(path)
		

	
def timer(func):
	
	def wrapper(*args, **kw):
		tStart = time.time()
		fct = func(*args, **kw)
		tEnd = time.time()
		logger.info('Spend %4fs'%(tEnd-tStart))		
		return fct
	return wrapper

def isSqr(number):
	_numSqrt = math.sqrt(number)
	_ceil = int(math.ceil(_numSqrt))
	_floor = int(math.floor(_numSqrt))
	result=True if _ceil == _floor else False
	return result, int(_numSqrt)
#(28-5+(2*0))/1+1 -> 24
#28-14->14->15
#21

@timer
def printMatrixE(a):
	print("Matrix["+("%d" %a.shape[0])+"]["+("%d" %a.shape[1])+"]")
	record = a.shape[0]
	rows = a.shape[1]
	cols = a.shape[2]
	print ("Total Row {0} and Column {1}".format(rows, cols))
	tmpAryStr = ""
	for i in range(0,rows):
		tmpAryStr = ""
		#print("row {0}".format(i))
		for j in range(0,cols):
			tmpAryStr += str(a[0,i,j])
			#print("column {0} value {1}".format(j,a[i,j] ))
		print(tmpAryStr)
	#print("")

#have to retest
def poolSize(imgSize, kSize, strides, padding=0):

	#strides=2
	logger.debug("strides is {0}".format(strides))
	#(28 - 5 + 0)/1 +1 ->23+1 ->24
	#(28-6) if stride is 2 ->11+2 ->13
	#therefore, the P-padding is 2
	
	tmpSize = imgSize-kSize+(2*padding)
	logger.debug("1 - oSize is {0}".format(tmpSize))
	mod=tmpSize%strides
	logger.debug("1.1 - Mod is {0}".format(mod))
	
	if mod == 0:
		oSize = (tmpSize//strides)+1
	else:
		logger.error("!!!ERROR : IMAGE RESHAPE ERROR!!!")
		logger.error("!!!    WRONG kernel/filter size {0}   !!!".format(kSize))
		sys.exit(1)

	logger.info("Shape Validator : Output Shape is {0}".format(oSize))
	
	return oSize