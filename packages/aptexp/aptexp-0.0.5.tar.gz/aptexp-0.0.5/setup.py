#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
"""
打包的用的setup必须引入，
"""
 
VERSION = '0.0.5'
 
setup(name='aptexp',
      version=VERSION,
      description="A tiny tools to export simple xls file from mongodb based on Python",
      long_description='',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python mongodb xls',
      author='Duolk',
      author_email='1229125444@qq.com',
      url='',
      license='Beihang',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'xlrd',
        'xlwt'
      ],
      entry_points={
        'console_scripts':[
            'aptexp = aptexpy.aptexp:export'
        ]
      },
)