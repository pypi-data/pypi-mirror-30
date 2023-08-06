# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 05:18:01 2018

@author: james
"""
#!/usr/bin/env python
from setuptools import setup, find_packages
from distutils.extension import Extension
import sys
import warnings


try:
    import numpy as np
except:
    build_requires = ['numpy']
    sys.exit("Please install numpy: pip install numpy")

useCy = True
try:
    from Cython.Build import cythonize
except ImportError:
    useCy = False
    warnings.warn("Cython not found. Cython Provides Speed Up and is recommended")


if(useCy):
    try:
        extensions = [
            Extension("globeos.utils.globefuncs", ["globeos/utils/cython/globefuncs.pyx"], include_dirs=[np.get_include()])
        ]
    
        setup(name='globeos',
              version='0.1.0',
              description='Package to display data on globe',
              author='James Driver',
              author_email='jad44@aber.ac.uk',
              url='https://github.com/JMDriver/GlobeOS',
              download_url='https://github.com/jmdriver/globeos/archive/0.1.0.tar.gz',
              packages=find_packages(exclude=('tests', 'docs', 'dist', 'build')),
              ext_modules = cythonize(extensions),
              setup_requires=build_requires,
              install_requires=[
                      'pygame==1.9.3',
                      'numpy',
                      'matplotlib',
                      'pillow>=2.1.0'
                      ]
             )
    except:
        setup(name='globeos',
              version='0.1.0',
              description='Package to display data on globe',
              author='James Driver',
              author_email='jad44@aber.ac.uk',
              url='https://github.com/JMDriver/GlobeOS',
              download_url='https://github.com/jmdriver/globeos/archive/0.1.0.tar.gz',
              packages=find_packages(exclude=('tests', 'docs', 'dist', 'build')),
              setup_requires=build_requires,
              install_requires=[
                  'pygame==1.9.3',
                      'numpy',
                      'matplotlib',
                      'pillow>=2.1.0'
              ]
    )        
    
else:
    setup(name='globeos',
          version='0.1.0',
          description='Package to display data on globe',
          author='James Driver',
          author_email='jad44@aber.ac.uk',
          url='https://github.com/JMDriver/GlobeOS',
          download_url='https://github.com/jmdriver/globeos/archive/0.1.0.tar.gz',
          packages=find_packages(exclude=('tests', 'docs', 'dist', 'build')),
          install_requires=[
              'pygame==1.9.3',
                  'numpy',
                  'matplotlib',
                  'pillow>=2.1.0'
          ]
)
    
