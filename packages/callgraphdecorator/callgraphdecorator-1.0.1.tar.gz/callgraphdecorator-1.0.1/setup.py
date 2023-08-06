#!/usr/bin/python3
__author__ = 'Jakub Pelikan'
from setuptools import setup
import callgraphdecorator

setup(
    name='callgraphdecorator',
    version=callgraphdecorator.__version__,
    description='Decorator for easy use PyCallGraph',
    long_description=open('README.rst').read(),
    url='https://github.com/p-eli/pycallgraphdecorator',
    author=callgraphdecorator.__author__,
    author_email=callgraphdecorator.__email__,
    keywords=['PyCallGraph', 'gui', 'access point'],
    include_package_data=True,
    license=open('LICENSE').read(),
    packages=['callgraphdecorator'],
    install_requires=['pycallgraph'],
    use_2to3=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
)
