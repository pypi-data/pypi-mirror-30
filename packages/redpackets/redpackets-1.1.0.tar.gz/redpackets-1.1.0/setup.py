# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.1.0'


setup(
    name='redpackets',
    version=version,
    keywords='',
    description='Red Packets Split Algorithm',
    long_description=open('README.rst').read(),

    url='https://github.com/Brightcells/redpackets',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['redpackets'],
    py_modules=[],
    install_requires=['monetary'],

    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
