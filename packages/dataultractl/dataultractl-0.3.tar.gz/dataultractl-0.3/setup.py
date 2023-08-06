# -*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

"""
打包的用的setup必须引入，
"""

VERSION = '0.3'

setup(name='dataultractl',
      version=VERSION,
      # package_data={'danmufm': ['template/*', ]},
      description="a tiny and smart cli player of dataultra based on Python",
      long_description='just enjoy',
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python dataultra du.cli terminal',
      author='du',
      author_email='du@huayun.com',
      url='http://10.131.40.141',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'requests',
          'prettytable'
      ],
      entry_points={
          'console_scripts': [
              'ductl = dataultractl.shell:main'
          ]
      },
      )
