# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 05:18:01 2018

@author: james
"""
#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from distutils.extension import Extension
import sys


try:
    import numpy as np
except:
    sys.exit("Please install numpy: pip install numpy")

useCy = True
try:
    from Cython.Build import cythonize
except ImportError:
    useCy = False
    sys.exit("Cython not found. Cython Provides Speed Up and is recommended")


if(useCy):
    extensions = [
        Extension("globeos.utils.globefuncs", ["globeos/utils/cython/globefuncs.pyx"], include_dirs=[np.get_include()])
    ]
    
    setup(name='globeos',
          version='0.0.7',
          description='Package to display data on globe',
          author='James Driver',
          author_email='jad44@aber.ac.uk',
          url='https://github.com/JMDriver/GlobeOS',
          download_url='https://github.com/jmdriver/globeos/archive/0.0.7.tar.gz',
          packages=find_packages(exclude=('tests', 'docs', 'dist', 'build')),
          ext_modules = cythonize(extensions),
          install_requires=[
                  'pygame==1.9.3',
                  'numpy',
                  'matplotlib',
                  'pillow>=2.1.0'
                  ]
         )
    
else:
    setup(name='globeos',
          version='0.0.7',
          description='Package to display data on globe',
          author='James Driver',
          author_email='jad44@aber.ac.uk',
          url='https://github.com/JMDriver/GlobeOS',
          download_url='https://github.com/jmdriver/globeos/archive/0.0.7.tar.gz',
          packages=find_packages(exclude=('tests', 'docs', 'dist', 'build')),
          install_requires=[
              'pygame==1.9.3',
                  'numpy',
                  'matplotlib',
                  'pillow>=2.1.0'
          ]
)
    
