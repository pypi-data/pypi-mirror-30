# -*- codding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
from os.path import dirname
from os.path import join


setup(
    name='zhora',
    version='0.1.0',
    packages=find_packages(),
    author='Rash',
    author_email='rsh@tut.by',
    license='MIT',
    classifiers=[
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'fake-useragent>=0.1.10',
        'asyncio>=3.4.3',
        'aiohttp>=3.1.1',
        'lxml>=4.2.1',
    ]
)
