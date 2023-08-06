from setuptools import setup

setup(name='appml',
	packages=['appml'],
	version='0.1',
	description='ml fucntions for training',
	author='Jiannan (Leo) Liu',
	author_email='jiannan.liu.28@gmail.com',
	url='https://github.com/Jiannan28/appml',
	license='MIT',
	classifiers = [],
	install_requires=['pandas>=0.22.0',
	'numpy>=1.11.3',
	'scikit-learn>=0.19.1',
	'scipy>=1.0.0',
	'seaborn>=0.8.1',
	'matplotlib>=2.0.0'
	],
	zip_safe=False)

