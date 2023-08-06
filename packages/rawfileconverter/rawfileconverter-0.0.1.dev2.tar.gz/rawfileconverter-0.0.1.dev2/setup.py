""" 
Setup file for raw image converter

"""
from setuptools import setup,find_packages

__version__ = '0.0.1.dev2'
__author__ = 'Mahendran Narayanan'

requirements = [
	'rawpy==0.10.1',
	'imageio==2.2.0',
]

setup(
	name='rawfileconverter',
	version=__version__,
	description = 'Convert CR2 files to JPG',
	long_description='This package helps CANON users to convert images shot in CR2 mode to normal jpg which can be viewed easily in laptop',
	author=__author__,
	author_email='mahendrannnm@gmail.com',
	url='https://github.com/mahendran-narayanan/rawfileconverter',
	keywords='cr2 image rawfile canon converter jpg jpeg',
	license='MIT',
	classifiers=[
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python :: 3.6',
		'Topic :: Multimedia',
	],
	packages=find_packages('rawfileconverter'),
	install_requires=requirements,
)