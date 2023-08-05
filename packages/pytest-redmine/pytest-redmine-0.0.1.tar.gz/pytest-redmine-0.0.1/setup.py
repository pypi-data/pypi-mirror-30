#!/usr/bin/env python
# encoding UTF-8

from setuptools import setup
from setuptools import find_packages

def readme():
    with open('README.md', 'r') as readme_file:
        return readme_file.read()

setup(
    name='pytest-redmine',
    version='0.0.1',
    license='MIT license',
    description='Pytest plugin for redmine',
    long_description= readme(),
    author='Matthieu Herrmann',
    url='https://github.com/matisla/pytest-redmine',
    packages=['pytest_redmine'],
    entry_points = {
        'pytest11' : [
            'pytest-redmine = src.plugin',
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Testing',
    ],
    keywords=[
        'redmine', 'pytest', 'py.test'
    ],
    install_requires=[
        'pytest',
        'python-redmine'
    ],
    python_requires='>=3.6'
)
