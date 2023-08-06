from setuptools import setup, find_packages
#still have to review and test before distribution
#missing README file
#unclear install requirement, i.e. dill, numpy, pd
#could distribute toolbox module as trial 

setup(
	name='ronnie',
	version='1.8.1',
	license='MIT License',
	description='roNNie. A Lightweight AI Framework for Deep Learning.',
	author='Kevin Lok KaWing',
	author_email='kevinkwlok@gmail.com',
	keywords="AI, DeepLearning,CNN",
	packages=['ronnie','ronnie.lib','ronnie.lib.collector','ronnie.lib.designer','ronnie.lib.optimizer','ronnie.lib.monitor','ronnie.conf','ronnie.data','ronnie.template','ronnie.template.cnn','ronnie.examples','ronnie.logs'],
	
	package_data = {'ronnie.data' : ['./digitalRec/*.zip'] ,
					'ronnie.conf' : ['./*.json'],
					'ronnie.logs' : ['./*.log'],
					'ronnie.template' : ['./*.*'] ,  
					'ronnie.template.cnn' : ['./*.py'] ,
					'ronnie' : ['./LICENSE.txt'], 
					},
	install_requires=['tensorflow>=1.6','numpy>=1.14','pandas>=0.22'], #external packages as dependencies
	url='https://ronnie.ai',
	long_description=open('README.txt').read(),
	classifiers=[
		"Development Status :: 4 - Beta",
		"Topic :: Scientific/Engineering :: Artificial Intelligence",
		"License :: OSI Approved :: MIT License",
		],
	python_requires='>=3.6, <4',
	#Dev python 3.6.4
   )