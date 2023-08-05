#!/usr/bin/env python
#coding=utf-8

from setuptools import setup, find_packages

setup(
    name='morse for python',
    version='1.0',
    description=(
        'morse for python'
    ),
    long_description=open('README.rst').read(),
    author='derek sunder',
    author_email='sunder3344@sina.com',
    maintainer='derek sunder',
    maintainer_email='sunder3344@sina.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/sunder3344',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    keywords='morse for python'
)