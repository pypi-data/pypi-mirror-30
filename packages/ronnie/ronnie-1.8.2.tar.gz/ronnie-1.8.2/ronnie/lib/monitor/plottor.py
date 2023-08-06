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
import matplotlib.pyplot as plt

import 	ronnie.lib.monitor.logKeeper	as lk
import 	ronnie.lib.util				as util
import 	ronnie.meta 				as meta

logger = logging.getLogger("roNNie")		


def appendModelAcc(modelName, data):
	try:
		logger.info("......APPENDing Model Acc......")
		
		csvFullFilePath = util.getPath("stat",modelName)
		
		df=pd.DataFrame(data, index=[0], columns = ["steps","acc","loss"])
		
		if os.path.isfile(csvFullFilePath):
			df.to_csv(csvFullFilePath, mode='a', encoding="utf-8",index=False, header=False)
		else:
			df.to_csv(csvFullFilePath,mode='a', encoding="utf-8",index=False)

	except IOError as ioE:
		logger.error("I/O error({0})".format(ioE))
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except SystemExit:  
		pass  
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
	
def plotModelAcc(modelName,saveFig=True, withDistance=True,exportOnly=False):
#=design.modelDef[meta.MODEL_NAME]
	try:
		logger.info("......PLOTTing......")
		
		csvFullFilePath = util.getPath("stat", modelName)
		figFullFilePath = util.getPath("figures", modelName)
	
		csv = pd.read_csv(csvFullFilePath)
		
		data = csv[["steps", "acc", "loss"]]
		arrEvalSteps = data["steps"]
		arrEvalAcc = data["acc"]
		arrEvalDistance = data["loss"]
		
		#logger.debug("Data :arrEvalSteps = {0}".format(arrEvalSteps))
		#logger.debug("Data :arrEvalAcc = {0}".format(arrEvalAcc))
		#logger.debug("Data :arrEvalDistance = {0}".format(arrEvalDistance))

########################################################
#Plot the accurcy
##00e64d - light blue, #003366 - dark blue, #ff0066 - Fuchsia (a kind of light red)
########################################################		
		p1 = None
		p2 = None

		if withDistance:
			p1 = plt.subplot(211)
		else:
			p1 = plt.subplot(111)
		
		plt.suptitle("MODEL :" + modelName + " | STEPS :" + str(len(arrEvalSteps)), fontsize=16)
		plt.subplots_adjust(hspace=0.5)
		
		p1.plot(arrEvalSteps, arrEvalAcc,label="ACCURCY",color="#0066cc")
		#plot the trend
		z = np.polyfit(arrEvalSteps, arrEvalAcc, 4)
		p = np.poly1d(z)
		#coefs = poly.polyfit(x, y, 4)
		#ffit = poly.polyval(x_new, coefs)
		p1.plot(arrEvalSteps,p(arrEvalSteps), linestyle="--", label="ACC-TREND", color="#ff0066")
		
		#plot the closest line
		cLine = max(arrEvalAcc)
		p1.axhline(y=cLine, color="#003366", linestyle=':', label="MAX ACC")
		textXLoc = int(len(arrEvalSteps)/2)
		textSL = "MAX ACC : " + str(round(cLine,4))
		p1.text(arrEvalSteps[0], cLine, textSL, verticalalignment='top')
		
		#plot the max point
		iMax = np.argmax(arrEvalAcc)
		textLocX = -150 
		if iMax == 0: 
			textLocX = 30
			
		p1.annotate('Max Point:[{0}, {1}]'.format(arrEvalSteps[iMax], round(arrEvalAcc[iMax],4)), xy=(arrEvalSteps[iMax], arrEvalAcc[iMax]),  xycoords='data',
             xytext=(textLocX, -50), textcoords='offset points',
             size=8, ha='right', va="center",
             bbox=dict(boxstyle="round", alpha=0.1),
             arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.1));
		
		#plot the last point
		iLast = len(arrEvalAcc)
		iLast -= 1
		p1.annotate('Last Data:[{0}, {1}]'.format(arrEvalSteps[iLast], round(arrEvalAcc[iLast],4)), xy=(arrEvalSteps[iLast], arrEvalAcc[iLast]),  xycoords='data',
             xytext=(-30, -30), textcoords='offset points',
             size=8, ha='right', va="center",
             bbox=dict(boxstyle="round", alpha=0.1),
             arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.1));
		
		p1.set_title("ACCURACY STATISTIC")
		p1.set_xlabel("STEP (s)")
		p1.set_ylabel("ACCURCY")
		p1.legend()
		
########################################################
#Plot the distance
##00e64d - light green, #009933 - dark green, #ff3300 - orange
########################################################
		if withDistance:
			p2 = plt.subplot(212)
			p2.plot(arrEvalSteps, arrEvalDistance,label="DISTANCE", color="#00e64d")
			#plot the trend
			z = np.polyfit(arrEvalSteps, arrEvalDistance, 4)
			p = np.poly1d(z)
			#coefs = poly.polyfit(x, y, 4)
			#ffit = poly.polyval(x_new, coefs)
			#color=' coral ', linestyle=':', marker='|'
			p2.plot(arrEvalSteps,p(arrEvalSteps),linestyle="--", label="DIS-TREND", color="#ff3300")
			
			#plot the closest line
			cLine = min(arrEvalDistance)
			p2.axhline(y=cLine, color="#009933", linestyle=':', label="MAX DIS")
			textXLoc = int(len(arrEvalSteps)/2)
			textSL = "MIN DIS : " + str(round(cLine,4))
			p2.text(arrEvalSteps[0], cLine, textSL, verticalalignment='bottom')
			
			#plot the max point
			iMin = np.argmin(arrEvalDistance)

			textLocX = -150 
			if iMin == 0:
				textLocX = 80
			
				
			p2.annotate('Min Point:[{0}, {1}]'.format(arrEvalSteps[iMin], round(arrEvalDistance[iMin],4)), xy=(arrEvalSteps[iMin], arrEvalDistance[iMin]),  xycoords='data',
			xytext=(textLocX, 60), textcoords='offset points',
			size=8, ha='right', va="center",
			bbox=dict(boxstyle="round", alpha=0.1),
			arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.1));
			
			#plot the last point
			iLast = len(arrEvalDistance)
			iLast -= 1
			textLocY = 30
			if iLast == np.argmax(arrEvalDistance):
				textLocY = -50			
						
			p2.annotate('Last DataL[{0}, {1}]'.format(arrEvalSteps[iLast], round(arrEvalDistance[iLast],4)), xy=(arrEvalSteps[iLast], arrEvalDistance[iLast]),  xycoords='data',
            xytext=(-30, textLocY), textcoords='offset points',
            size=8, ha='right', va="center",
            bbox=dict(boxstyle="round", alpha=0.1),
            arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.1));			
			
			p2.set_title("DISTANCE STATISTIC")
			p2.set_xlabel("STEP (s)")
			p2.set_ylabel("DISTANCE")
			p2.legend()
#########################################################		
		
		logger.info("......EXPORTing figure......")		
		if saveFig:
			plt.savefig(figFullFilePath)
		if not exportOnly:
			plt.show()
		plt.close()
		
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