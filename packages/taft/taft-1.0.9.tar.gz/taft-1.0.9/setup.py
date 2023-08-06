from setuptools import setup

setup( 
	name = 'taft',
	version = '1.0.9',
	description = 'Technical analysis and research&simulation framework for algorithmic traders',
	url = 'http://github.com/Savahi/taft',
	author = 'Savahi',
	author_email = 'sh@tradingene.ru',
	license = 'MIT',
	classifiers=[
	    'Development Status :: 3 - Alpha',
	    'Intended Audience :: Developers',
	],	
	packages = ['taft'],
	keywords = 'technical analysis trading stock exchange',
	install_requires = ['numpy', 'datetime', 'os', 'cPickle'],
	include_package_data=True,
	zip_safe = False )


