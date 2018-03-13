#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='django-automationcommon',
    version='1.18',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description=(
        'Common functionality across different Django projects of the UofC UIS Automation team'
    ),
    long_description=open('README.rst').read(),
    url='https://github.com/uisautomation/django-automationcommon.git',
    author='Automation team, University Information Services, University of Cambridge',
    author_email='automation@uis.cam.ac.uk',
    tests_require=['testfixtures'],
    install_requires=[
        'django>=1.8,<2.1',
        'django-ucamlookup>=1.9.2',
        'django-ucamwebauth>=1.4.5',
        'requests',
        'celery<4',
        'python-dateutil',
        'zeep',
        'django-hijack',
        'django-stronghold',
        'beautifulsoup4',
        'mock',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
