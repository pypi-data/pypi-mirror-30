#!/usr/bin/env python

# To use a consistent encoding
from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-import-export-xml',
    version='0.1',
    description='An XML export format for django-import-export',
    long_description=long_description,
    author='Maykin Media',
    author_email='support@maykinmedia.nl',
    url='https://github.com/maykinmedia/django-import-export-xml',
    install_requires=[
        'dicttoxml',
        'django-import-export',
    ],
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    zip_safe=False,
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-django',
        'pytest-pep8',
        'pytest-pylint',
        'pytest-pythonpath',
        'pytest-runner',
    ],
    extras_require={
        'docs': [
            'sphinx',
            'sphinx_rtd_theme'
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ]
)
