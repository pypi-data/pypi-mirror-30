#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(name='archub',
    version='1.0.0a3',
    install_requires=[
        'requests',
        'pygithub',
        'gitpython',
    ],
    author='Don Grote',
    author_email='dgrote@refirmlabs.com',
    url='https://github.com/rfldong/archub',
    scripts=[
        'scripts/archub',
        'scripts/ah',
    ],
    packages=find_packages(exclude=['tests']),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Topic :: Software Development",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)
