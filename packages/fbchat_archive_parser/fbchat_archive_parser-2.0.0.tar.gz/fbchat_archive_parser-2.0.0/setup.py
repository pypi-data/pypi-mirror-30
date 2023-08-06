#! /usr/bin/env python
from setuptools import setup, find_packages
from io import open
import versioneer

setup(
    name='fbchat_archive_parser',
    packages=find_packages(exclude=["tests"]),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='A library/command line utility for parsing Facebook chat history',
    long_description=open('README.rst').read(),
    author='Dillon Dixon',
    author_email='dillondixon@gmail.com',
    url='https://github.com/ownaginatious/fbchat-archive-parser',
    license='MIT',
    keywords=['facebook', 'chat', 'messenger', 'history'],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=[line.strip()
                      for line in open("requirements.txt", "r",
                                       encoding="utf-8").readlines()],
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "fbcap = fbchat_archive_parser.main:fbcap",
        ],
    },
)
