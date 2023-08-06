#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# Version      : dev01
# Summary      : To handle logging 
#############################################################################################
import os
import sys
import json
import logging.config
import ronnie.meta as meta
import ronnie.lib.util as util

logger = logging.getLogger("roNNie")
#such cofiguration used to save the log to files

def initial(projPath,type="proj", logLevel=logging.INFO):
	logger.info("Project Path {0}".format(projPath))

	if type == meta.SYS:
		logging.basicConfig(level=logLevel)
	else:
		#meta.PROJECT_PATH		:"e:/kaggle/",
		logsPath = projPath + "./logs/"
		logDictPath = projPath + "./conf/"
		logDictFile = "logConf.json"
		tensorLogFile = "tensorflow.log"
	
		cfgPath = os.path.realpath(logDictPath + logDictFile)
		tensorLogPath = os.path.realpath(logsPath + tensorLogFile)
		
		if os.path.exists(cfgPath):
			with open(cfgPath, 'rt') as f:
				config = json.load(f)
				logging.config.dictConfig(config)
				logging.info("Initial DictConf for LK done.")
		else:
			logging.basicConfig(level=logLevel)
			logging.error("Can't Read config file, use BasicConfig")
			
		try:
			tLog = logging.getLogger('tensorflow')
			tLog.setLevel(logLevel)
			formatter = logging.Formatter('%(message)s')
			fh = logging.FileHandler(tensorLogPath)
			fh.setLevel(logLevel)
			fh.setFormatter(formatter)
			tLog.addHandler(fh)
			
		except IOError as iE:
			logger.error("File IO Error")
		except:
			logger.error("INITIAL - Unexpected error: {}".format(sys.exc_info()[0]))
##def setLevel(level):
##	levelDict = { 	meta.LOG_LEVEL_CRITICAL 	: 50, 
##					meta.LOG_LEVEL_ERROR		: 40,
##					meta.LOG_LEVEL_WARNING		: 30,
##					meta.LOG_LEVEL_INFO			: 20,
##					meta.LOG_LEVEL_DEBUG		: 10,
##					meta.LOG_LEVEL_NOTSET		: 0,
##					}
##	logger.setLevel(logging.INFO)
##	logging.setLevel(levelDict[level])
##	return
##					