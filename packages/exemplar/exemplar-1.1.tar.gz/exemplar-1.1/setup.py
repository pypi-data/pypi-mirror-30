#!/usr/bin/env python

from distutils.core import setup

setup(name='exemplar',
      version='1.1',
      description='Programming by Example',
      author='Amin Manna',
      author_email='manna@mit.edu',
      url='https://github.com/manna/exemplar',
      packages=['exemplar', 'exemplar.transforms'],
      install_requires=[
          'pycosat',
      ],
     )