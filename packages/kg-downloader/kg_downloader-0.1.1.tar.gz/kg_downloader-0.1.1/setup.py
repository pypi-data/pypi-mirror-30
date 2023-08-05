#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

VERSION = "0.1.1"

setup(name='kg_downloader',
      version=VERSION,
      description="a python tool which download songs from kg.qq.com.",
      long_description='',
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Terminals"
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python3 terminal downloader',
      author='justin13',
      author_email='justin13wyx@gmail.com',
      url="https://github.com/Justin13wyx/Python_Tools",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'requests',
        'lxml'
      ],
      entry_points={
        'console_scripts':[
            'kg_downloader = kg_downloader.main:main'
        ]
      },
)
