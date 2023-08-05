#!/usr/bin/env python

from setuptools import find_packages, setup

__version__ = '1.0'

requires = [
    'arrow==0.12.1',
    'emails==0.5.15',
    'PyMySQL==0.8.0',
    'redis==2.10.6',
    'schematics==2.0.1',
    'SQLAlchemy-Utils==0.33.1',
    'SQLAlchemy==1.2.1',
    'toml==0.9.4',
]

setup(
    name='dqpy',
    version=__version__,
    description='Danqing core Python library',
    author='Danqing Liu',
    author_email='code@danqing.io',
    url='https://github.com/danqing/dqpy',
    packages=find_packages(),
    install_requires=requires,
    zip_safe=True,
)
