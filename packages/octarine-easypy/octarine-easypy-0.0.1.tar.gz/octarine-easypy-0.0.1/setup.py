#!/usr/bin/env python

from distutils.core import setup

setup(name='octarine-easypy',
      version='0.0.1',
      description='easypy is a collection of python modules that makes developers happy. Based on commit 4a431f4',
      author='Ofer Koren',
      author_email='koreno@gmail.com',
      url='https://github.com/weka-io/easypy',
      license='BSD',
      packages=['easypy'])

# how to upload a package:
# 0. increment the version above
# 1. python setup.py register
# 2. python setup.py sdist upload
