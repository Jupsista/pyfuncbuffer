#!/usr/bin/env python

from distutils.core import setup


setup(
    name='pyFuncBuffer',
    version='0.1',
    packages=['pyfuncbuffer', ],
    license='GPLv3',
    description="A library for buffering function calls",
    long_description=open('README.txt').read(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Typing :: Typed"
        "Topic :: Software Development :: Libraries",
    ]
)
