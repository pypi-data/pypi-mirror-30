#!/usr/bin/env python
from setuptools import setup, find_packages
import pony_unitfield


def read_file(name):
    with open(name) as fd:
        return fd.read()

keywords = ['django', 'models', 'fields', 'unit', 'decimal', 'float']

setup(
    name='pony-unitfield',
    version=pony_unitfield.__version__,
    description=pony_unitfield.__doc__,
    long_description=read_file('README.rst'),
    author=pony_unitfield.__author__,
    author_email=pony_unitfield.__email__,
    # install_requires=read_file('requirements.txt'),
    license='BSD',
    url=pony_unitfield.__url__,
    keywords=keywords,
    packages=find_packages(exclude=[]),
    include_package_data=True,
    test_suite='runtests.main',
    tests_require=read_file('requirements-tests.txt'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
