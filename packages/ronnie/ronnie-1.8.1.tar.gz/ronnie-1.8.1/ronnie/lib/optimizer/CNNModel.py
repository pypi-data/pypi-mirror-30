#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# Version      : dev01
# Summary      : CNNModel Constructor : integrated to TensorFlow
#			   : Transform *multi*,*auto detected sizes* images from csv by 1 line of code
# Description  : Default Input Format:1st column : Label, the rest of columns : Image Pixels 
#############################################################################################
import sys
import pandas 				as pd
import numpy 				as np
import logging

import tensorflow 			as tf

import 	ronnie.meta 					as meta
import 	ronnie.lib.util 				as util
import  ronnie.lib.monitor.custError	as cError

import 	ronnie.lib.monitor.logKeeper  	as lk
import  ronnie.lib.monitor.plottor		as plottor

#lk.initial()

logger = logging.getLogger("roNNie")

def activationFct(act):
	logger.debug("activationFct input {0}".format(act))
	result = None 
	if act == meta.MODEL_ACT_RELU:
		result = tf.nn.relu
	elif act == meta.MODEL_ACT_SIGMOID:
		result = tf.sigmoid
	elif act == meta.MODEL_ACT_TANH:
		result = tf.tanh
	else:
		result = None
	
	logger.debug("activationFct result {0}".format(result))
	return result

def convLyr(imgXs, kernel,filter,padding,activation=tf.nn.relu):
	try:
		tensorImgXs = imgXs
		
		#Testing use, work well : 
		#CNNModel.printMatrixE(inputImgs)
		#CNNModel.printMatrixE(input_layer)
		
		conv = tf.layers.conv2d(
		inputs=tensorImgXs,
		filters=filter,
		kernel_size=[kernel,kernel],
		padding=padding,
		activation=activation)
		
		logger.info("CNN Convolutional Layer was built : {0}".format(conv))
		#CNNModel.printMatrixE(baz)
			
		return conv
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

# Pooling Layer 
# Example:
# Second max pooling layer with a 2x2 filter and stride of 2
# Input Tensor Shape: [batch_size, x, x, 16]
# Output Tensor Shape: [batch_size, x, x, 32]
# Would be better to define several poolsize and strides
def poolLyr(conv, size, strides):
	try:
		
		logger.info("Input p size {0}".format(size))
		pool = tf.layers.max_pooling2d(inputs=conv, pool_size=[size, size], strides=strides)

		logger.info(" CNN Pool Layer was built : {0}".format(pool))
		
		return pool
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

# Dense Layer
# Example:
# Densely connected layer with 1024 neurons
# Input Tensor Shape: [batch_size, 7 * 7 * 64]
# Output Tensor Shape: [batch_size, 1024]
#inputs=pool2_flat (default) , pool1_flat changed to 1 layer
#try to submit optDict to DenseOpt
# units=10
def denseLyr(flatInput,optDict,index):
	try:
		logits = None 
		activation = None
		name = 'DENSE' + str(index)
		
		activation = activationFct(optDict[meta.MODEL_ACT])
		
		logger.debug ("actvation result is {0}".format(activation))
		tInput = flatInput
		if not float(optDict[meta.MODEL_DROPOUTRATE]) < 0:
			tInput = tf.layers.dropout(inputs=flatInput, rate=optDict[meta.MODEL_DROPOUTRATE], training=True)
		#	logits = tf.layers.dense(inputs=dropout, units=optDict[meta.MODEL_NEURON],name=name)
		else:
			raise VaueError("DROPOUT RATE INCORRECT")
		if activation is None:
			logits = tf.layers.dense(inputs=tInput, units=optDict[meta.MODEL_NEURON],name=name)
			logger.info("AcTIVATION IS NONE")
		else:
			logits = tf.layers.dense(inputs=tInput, units=optDict[meta.MODEL_NEURON], activation=activation,name=name)
			logger.info("AcTIVATION NOT NONE")
				
		logger.info(" CNN Dense Opt logits was built : {0}".format(logits))
		
		return logits
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

#optDict Structure
# Logits layer
# Input Tensor Shape: [batch_size, 1024]
# Output Tensor Shape: [batch_size, 10]

def lyrMgr(imgXs, modelTower):
	try:
		if len(modelTower) == 0:
			raise cError.ModelError("No Defined Layer. Please check Model Tower.")
		
		imgXs = tf.cast(imgXs, tf.float32)
		
		for index in range(len(modelTower)):
			spec = modelTower[index][meta.LAYER_SPEC]
			logger.info("Spec : {0}".format(spec))
			input = imgXs
			denseLyrCounter = 0
			if not index == 0:
				input = modelTower[index-1][meta.LAYER_BRICK]
				
			if spec[meta.LAYER_TYPE] == meta.CONV_LAYER:
				logger.info("Index : {0}, CON : Lyr Type {1}".format(index,spec[meta.LAYER_TYPE] ))
				conv = convLyr(input, spec[meta.CON_KERNAL], spec[meta.CON_FILTER], spec[meta.CON_PADDING])
				modelTower[index][meta.LAYER_BRICK] = conv
			elif spec[meta.LAYER_TYPE] == meta.POOL_LAYER:
				logger.info("Index : {0}, Pool : Lyr Type {1}".format(index,spec[meta.LAYER_TYPE] ))
				pol = poolLyr(input, spec[meta.POOL_KERNAL], spec[meta.POOL_STRIDE])
				modelTower[index][meta.LAYER_BRICK] = pol
			elif spec[meta.LAYER_TYPE] == meta.DENSE_LAYER:
				logger.info("Index : {0}, DENSE : Lyr Type {1}".format(index,spec[meta.LAYER_TYPE] ))
				denseLyrCounter += 1
				if index == 0 or not modelTower[index-1][meta.LAYER_SPEC][meta.LAYER_TYPE] == meta.DENSE_LAYER:
					logger.info("ModelTower : Dense Layer before flatten : {0}".format(input))
					logger.info("ModelTower : Dense Layer input shape : {0}".format(input.get_shape()))
					logger.info("ModelTower : Dense Layer input shape : {0} | {1} | {2}  ".format(input.get_shape()[1],input.get_shape()[2],input.get_shape()[3] ))
					flattenShape = input.get_shape()[1]*input.get_shape()[2]*input.get_shape()[3] 
					logger.info("ModelTower : Dense Layer expected flatten shape : {0} ".format(flattenShape ))
					
					logger.info("ModelTower : Dense Layer before flatten : {0}".format(input))
					input = tf.reshape(input , [-1,flattenShape])
					# bugs at layers.flatten
					#input = tf.contrib.layers.flatten(input)
					logger.info("Data Flattening : Shape {0}".format(input ))
				
				dense = denseLyr(input, spec, index)
				modelTower[index][meta.LAYER_BRICK] = dense					
			else:
				raise cError.ModelError("Layer Type is missing")
				
		
		logger.info("ModelTower was built. Details:")
		for index in range(len(modelTower)):
			logger.info("Layer-{0}".format(index))
			logger.info("lyr Spec  : {0}".format(modelTower[index][meta.LAYER_SPEC]))			
			logger.info("lyr brick : {0} ".format(modelTower[index][meta.LAYER_BRICK]))	
		
		if denseLyrCounter < 1:
			raise cError.ModelError("No Dense Layer. Please Review the Model Tower.")
			
		return modelTower
	except cError.ModelError as mE:
		logger.error("ERROR : {0}".format(mE))
		sys.exit(1)
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise  

def initialEnvironment():
	with tf.Session() as sess:	
		logger.info("Start Initial Evironment...")
		init_op = tf.global_variables_initializer()
		logger.info("init_op is {0}".format(init_op))
		sess.run(init_op)
		logger.info("Session initialized")
		
def initialModel(imgXs,modelDef):

	dataCfg = modelDef[meta.DATA_CONFIG]
	modelTower = modelDef[meta.MODEL]
	graph = tf.Graph()
	
	ph_imgXs = None
	ph_labelYs = None
	
	ph_imgXs = tf.placeholder(tf.float32, shape=(None,dataCfg[meta.DATA_IMGX_WIDTH],dataCfg[meta.DATA_IMGX_HEIGHT],dataCfg[meta.DATA_IMGX_CHANNEL]))
	ph_labelYs = tf.placeholder(tf.int32, shape=(None,dataCfg[meta.DATA_LABELY_CLASSs]))
	
	modelTower = lyrMgr(ph_imgXs,modelTower)
	
	logger.info("imgXs obj {0}".format(imgXs))	
	logger.info("Trying Model with PH")
#	modelTower = modelDef[meta.MODEL]
	phLogits = modelTower[len(modelTower)-1][meta.LAYER_BRICK]
	
	logger.info("Trying Model with PH")
	
	with tf.Session() as sess:	
		a = sess.run(phLogits,feed_dict={ph_imgXs:imgXs})
	
	logger.info("Success")
	
	return modelTower

def tryModel(imgXs, modelDef):
	logger.info("Trying Model with PH")
	modelTower = modelDef[meta.MODEL]
	phLogits = modelTower[len(modelTower)-1][meta.LAYER_BRICK]
	with tf.Session() as sess:
		modelTower = sess.run(phLogits,feed_dict={"ph_imgXs":imgXs*1.0})
	logger.info("Trying Model with PH")
	return
######after 1.1.x version	
def run(features, labels, mode, params):
	imgXs = features
	logger.info("at RUN: CHECK TYPE: InputX(dtype) : {0} ".format(features.dtype))

	modelTower = params[meta.MODEL]
	#BUILD CNNMODEL
	logging.debug("imgXs shape {0}".format(imgXs.shape))
	
	modelTower = lyrMgr(imgXs,modelTower)
#	modelTower = lyrMgr(ph_imgXs,modelTower)
	
	logger.debug("len of modelTower : {0} ".format(len(modelTower)))
	
	logits = modelTower[len(modelTower)-1][meta.LAYER_BRICK]

	#End : Structure of CNN
	logger.info("Logits is {0}".format(logits))
			
	if mode == tf.estimator.ModeKeys.TRAIN:		
		learning_rate = None
				
		if meta.MODEL_LEARNRATE in dict(params):
			learning_rate = params[meta.TRAIN_CONFIG][meta.MODEL_LEARNRATE] 
		else:
			learning_rate = 0.001		
		
		distance = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
	
	
####ADAM and GD are the optimizers good at begining
		if params[meta.TRAIN_CONFIG][meta.OPTIMIZER] == meta.OPTIMIZER_ADAM:
			optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)	
		elif params[meta.TRAIN_CONFIG][meta.OPTIMIZER] == meta.OPTIMIZER_GD:
			optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)	
		
		################################################################
		#optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
		#rho: tensor或者浮点数. The decay rate. 
		#add decay rate(rho) for Adadelta
		#tf.train.AdagradOptimizer(learning_rate				, initial_accumulator_value=0.1, use_locking=False, name=’Adagrad’)
		#tf.train.MomentumOptimizer(learning_rate				, momentum, use_locking=False, name=’Momentum’, use_nesterov=False)
		#tf.train.AdadeltaOptimizer.init(learning_rate=0.001	, rho=0.95, epsilon=1e-08, use_locking=False, name=’Adadelta’)
		#tf.train.RMSPropOptimizer(learning_rate				,decay=0.9, momentum=0.0, epsilon=1e-10,use_locking=False, name=’RMSProp’)
		#tf.train.AdamOptimizer(learning_rate=0.001				, beta1=0.9, beta2=0.999, epsilon=1e-08, use_locking=False, name=’Adam’)
		#tf.train.FtrlOptimizer(learning_rate					, learning_rate_power=-0.5, initial_accumulator_value=0.1, l1_regularization_strength=0.0,l2_regularization_strength=0.0,use_locking=False, name=’Ftrl’)
		################################################################
		train_op = optimizer.minimize(loss=distance,global_step=tf.train.get_global_step())
		
		logger.info("CHECK TYPE: logits(dtype):{0}".format(logits.dtype))
		
		####testinggggggg 20180405
		
##		if params[meta.BASIC_CONFIG][meta.BYTES]==meta.BYTES32:
## and lyrMgr has casting of dType
		
		predicts = tf.argmax(input=(logits), axis=1,output_type=tf.int32)
		logger.info("CHECK TYPE: LabelYs(dtype):{0}, predictYs(dtype):{1}".format(labels.dtype, predicts.dtype))
		
		tf.cast(predicts, tf.int32)
		logger.info("CHECK TYPE: LabelYs(dtype):{0}, predictYs(dtype):{1}".format(labels.dtype, predicts.dtype))
		
		acc = tf.equal(labels, predicts)
		accRMean = tf.reduce_mean(tf.cast(acc, tf.float32))
		logger.info("accuracy mean: {0}".format(accRMean))
		
		#accOpt = tf.metrics.accuracy(labels=labels, predictions=predicts, name='accOpt')
		#metrics = {'Acc': accOpt}
		#eval_metric_ops = { "accuracy" : metrics }

		train_group = tf.group(train_op, {"AccRMean" : accRMean})
		logger.info("accRMean : {0}".format(accRMean))
		
		#logging_hook = tf.train.LoggingTensorHook({"3D-Distance" : distance}, every_n_iter=1)
		logging_hook = tf.train.LoggingTensorHook({"3D-Distance" : distance,"AccReduceMean": accRMean, "Acc": acc, "Predicts" : predicts }, every_n_iter=1)
		predictions={
				'classes': tf.argmax(logits, axis=1) ,
				'predictions': tf.nn.softmax(logits,name="softmax_tensor")           
		}				
		return tf.estimator.EstimatorSpec(mode=mode,  predictions=predictions, loss=distance, train_op=train_group,  training_hooks = [logging_hook])
	
#add comments		
	elif mode == tf.estimator.ModeKeys.EVAL:

		distance = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
		predicts = tf.argmax(input=(logits), axis=1)
		accuracy = tf.metrics.accuracy(labels=labels,
                              predictions=predicts, name='accuracyOpt')
		metrics = {'accuracy': accuracy}

		#eval_ops = {"accuracy": tf.metrics.accuracy(labels=labels, predictions=predictions["classes"])}
		return tf.estimator.EstimatorSpec(mode=mode, loss=distance, eval_metric_ops=metrics)
		

#add comments
	elif mode == tf.estimator.ModeKeys.PREDICT:

		predicts = tf.argmax(input=(logits), axis=1)
		predictions = {'class_ids': predicts[:, tf.newaxis],
						'probabilities': tf.nn.softmax(logits),'logits': logits,}

		return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)
	else:
		logger.ERROR("!!! WRONG MODE !!!")
		return

def trainN(imgXs, labelYs, paramDict, batch, steps):
	try:
		logger.info("Part 4: Training")
		results=None
		with tf.Session() as sess:
		
			logger.info("Initializing TF variables : SESS_accRMean")
		
			mnist_classifier = tf.estimator.Estimator(model_fn=run,params=paramDict, model_dir="./models/" + paramDict[meta.MODEL_NAME])
			
			logger.info("################################################################")	
			logger.info("Classifier Constructed")
			logger.info("batch = {0} steps = {1}".format(batch, steps))
			logger.info("ImgXs Shape = {0} LabelYs Shape = {1}".format(imgXs.shape, labelYs.shape))
			inputFn = tf.estimator.inputs.numpy_input_fn(x=imgXs, y=labelYs, 
															batch_size=batch, 
															num_epochs=None, shuffle=paramDict[meta.TRAIN_CONFIG][meta.SHUFFLE])
			####Training part
#log hook at	 training?
			#tensors_to_log = None
			#logging_hook = tf.train.LoggingTensorHook(tensors=tensors_to_log, every_n_iter=100)
			logger.info("training start")
			#, hooks=[logging_hook]
			result = mnist_classifier.train(input_fn=inputFn, steps=steps)
	
		logger.info("training end")
		
		logger.info("Enjoy! Email us your comments and credits. Thanks.")
		return result

	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
		raise
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
			


def modelEval(imgXs, labelYs, paramDict):
#evaluation_hooks
	try:

		logger.info("Part 5: Evaluate")
		results=None
		with tf.Session() as sess:
			mnist_classifier = tf.estimator.Estimator(model_fn=run, params=paramDict, model_dir="./models/" + paramDict[meta.MODEL_NAME])
			
			evalInputFn = tf.estimator.inputs.numpy_input_fn(x=imgXs,y=labelYs,
													num_epochs=1,shuffle=paramDict[meta.EVAL_CONFIG][meta.SHUFFLE])
			
			#Classifier is different from Predict
			results = mnist_classifier.evaluate(input_fn=evalInputFn)
			
		logger.debug("eResult : {0}".format(results))
		return results
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

		
def predictExport(pResults, modelDef):
	try:	
		predictions = list(pResults)
		predicted_classes = [p["class_ids"] for p in predictions]
		df=pd.DataFrame(predicted_classes, columns = ["Label"])
		df.insert(0, 'ImageId', range(1, len(df)+1))
		
		exportFullFilePath = util.getPath("exportPredict",modelDef[meta.MODEL_NAME])
		
		df.to_csv(exportFullFilePath, encoding=modelDef[meta.BASIC_CONFIG][meta.MODEL_EXPORT_ENCODE],index=False)
		
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise	

def modelPredict(imgXs, labelYs, modelDef, export=True):
	try:
		logger.info("Part 6: Predict")
		results = None
		modelDef[meta.TRAIN_CONFIG]
		with tf.Session() as sess:

			mnist_classifier = tf.estimator.Estimator(model_fn=run, params=modelDef, model_dir="./models/" + modelDef[meta.MODEL_NAME])
			
			inputPredictFn = tf.estimator.inputs.numpy_input_fn(x=imgXs,y=labelYs,
																				num_epochs=1,shuffle=False)
			
			#Classifier is different from Eval			
			pResults = mnist_classifier.predict(input_fn=inputPredictFn)
			
			logger.debug("pResult is {0}".format(pResults))
			
		if export:
			predictExport(pResults, modelDef)
			logger.info("Finished. PREDICTION data exported to {0}".format(modelDef[meta.BASIC_CONFIG][meta.MODEL_EXPORT_FILE]))
		
		logger.info("Enjoy! Email us your comments and credits. Thanks.")
		return pResults
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
		
def trainNeval(trainData,evalData, modelDef, cycles=50, samples=5000, steps=1, withEval=True, evalSteps=10,exportOnly=True):
	try:
		arrEvalAcc = []
		arrEvalSteps = []
		eResult = None
		logger.info("at trainNeval: CHECK TYPE: InputX(dtype) : {0} | LabelYs(dtype):{1}".format(trainData[meta.DATA_INPUTXs].dtype, trainData[meta.DATA_LABELYs].dtype))
	
		for index in range (0, cycles):
			logger.info("#############################################################")
			logger.info("Start : Part 2.3: Training Cycle {0}".format(cycles))
			tResult = trainN(trainData[meta.DATA_INPUTXs],trainData[meta.DATA_LABELYs], modelDef, samples, steps)
			logger.info("tResult :{0}".format(tResult))

			logger.info("#############################################################")
			logger.info("Finished : Part 2.3: Training.{0}".format(tResult))
#############################################################		
#############Evaluation######################################
#############################################################
			logger.info("Start : Part 2.2: Model Evaluation.")
	
			logger.debug("Evaluation imgXs   Shape: {0} ".format(evalData[meta.DATA_INPUTXs].shape))
			logger.debug("Evaluation LabelYs Shape: {0} ".format(evalData[meta.DATA_LABELYs].shape))
			
			if withEval and index % evalSteps == 0:
				eResult = modelEval(evalData[meta.DATA_INPUTXs], evalData[meta.DATA_LABELYs], modelDef)
				
				plottor.appendModelAcc(modelDef[meta.MODEL_NAME], {"steps": eResult['global_step'],"acc" :eResult['accuracy'],"loss" : eResult['loss']})
				plottor.plotModelAcc(modelDef[meta.MODEL_NAME],exportOnly=exportOnly)
		
		
		logger.info("Enjoy! Email us your comments and credits. Thanks.")
		return eResult
	
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
####################		
def main():
	return
if __name__ == "__main__":
 # if you call this script from the command line (the shell) it will
 # run the 'main' function
	main()	