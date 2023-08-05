# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 16:16:20 2018

@author: clementsw
"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='universal_interferometer',
      version='0.1',
      description='Algorithms for universal interferometers',
      long_description='Decompose unitary matrices into interferometers using two different algorithms, and visualize the interferometers',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Physics',
      ],      
      url='http://github.com/clementsw/universal_interferometer',
      author='William R. Clements',
      author_email='mail@william-clements.com',
      license='MIT',
      packages=['universal_interferometer'],
      install_requires=[
          'numpy',
          'matplotlib',
      ],
      include_package_data=True,
      zip_safe=False)