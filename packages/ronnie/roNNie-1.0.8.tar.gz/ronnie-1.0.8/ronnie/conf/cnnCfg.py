import ronnie.meta 					as meta


basicCfg = {		meta.PROJECT_PATH		: "",
				meta.MODEL_EXPORT_FILE	: "./export/result.csv",
				meta.MODEL_EXPORT_ENCODE: "utf-8",
			}
# comments to figure out the usage of dataCfg
# You can check the data structure by data.shape
dataCfg = 	{	meta.DATA_IMGX_WIDTH	: 28, 
				meta.DATA_IMGX_HEIGHT 	: 28, 
				meta.DATA_IMGX_CHANNEL	: 1, 
				meta.DATA_LABELY_CLASSs	: 10,
			}

trainCfg = {	meta.MODEL_LEARNRATE   	: 0.0001,
				#Support GD, ADAM (OPTIMIZER_GD, meta.OPTIMIZER_ADAM) Optimizer
				meta.OPTIMIZER			: meta.OPTIMIZER_ADAM,
				meta.SHUFFLE 	    	: True,
			}
evalCfg = {		meta.SHUFFLE 	    	: True,
			}		