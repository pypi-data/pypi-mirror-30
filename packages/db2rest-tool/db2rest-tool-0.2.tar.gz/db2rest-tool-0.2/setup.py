#-*- coding: utf-8 -*-

from setuptools import setup

setup(name='db2rest-tool',
      version='0.2',
      author='oliveirabrunoa',
      author_email='oliveirabrunoa@gmail.com',
      url='https://github.com/oliveirabrunoa/db2rest',

      packages=['DB2Rest'],

      scripts=['scripts/execute_db2rest'],
)
