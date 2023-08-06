# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '1.0.1'

setup(name='timeunit',
      version=version,
      description="timeunit",
      long_description='',
      keywords='timeunit',
      author='Ralph-Wang',
      author_email='ralph.wang1024@gmail.com',
      url='https://github.com/Ralph-Wang/timeunit-python',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      py_modules=['timeunit'],
      zip_safe=False,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
