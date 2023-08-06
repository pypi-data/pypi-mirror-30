import codecs
import os
import sys

try:
	from setuptools import setup, find_packages
except:
	from distutils.core import setup



def read(fname):
	return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_des = read("README.rst")
    
platforms = ['linux/Windows']
classifiers = [
    'Development Status :: 3 - Alpha',
    'Topic :: Text Processing',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
]

install_requires = [
    'numpy == 1.14.0',
    'pandas == 0.22.0',
    'sklearn',
    'xgboost',
    'lightgbm',
    'datetime',
    'pandasql'
]

    
setup(name='Optiation',
      version='0.3.4',
      description='A Python package that used to forecast system deployment to Inter-Credit.',
      long_description=long_des,
      py_modules=['optiation/models','optiation/pylog'],
      author = "DataXujing",  
      author_email = "xujing@inter-credit.net" ,
      url = "https://dataxujing.github.io" ,
      license="Apache License, Version 2.0",
      platforms=platforms,
      classifiers=classifiers,
      install_requires=install_requires,
      include_package_data=True,
      package_data = {'optiation': ['data/*.xlsx'],'pic':['*.png']}

      )   
      
  