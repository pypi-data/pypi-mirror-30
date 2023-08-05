#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tec.ic.ia.pc1.g07',
      version='1.1.0',
      py_modules=['tec.ic.ia.pc1.g07'],
      description='Generador de muestras basados en los resultados electorales presidenciales de la primera ronda en Costa Rica.',
      author='Trifuerza',
      author_email='',
      url='https://github.com/mamemo/PC1',
      packages= find_packages(exclude=['docs', 'tests*']),
     )

      

      
