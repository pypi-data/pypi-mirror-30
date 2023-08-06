#!/usr/bin/env python
from setuptools import setup
import io

with io.open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='pyldapi',
    packages=['pyldapi'],
    version='0.1.3',
    description='A library for enabling Linked Data API functionality on top of Flask',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Nicholas Car',
    author_email='nicholas.car@csiro.au',
    url='http://github.com/CSIRO-enviro-informatics/pyldapi',
    download_url='https://github.com/CSIRO-enviro-informatics/pyldapi/archive/0.1.3.tar.gz',
    python_requires=">=3.0",
    keywords=['Linked pData API', 'Flask', 'HTTP API'],
    install_requires=[
        'Flask>=0.12.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/CSIRO-enviro-informatics/pyldapi/issues',
        'Source': 'https://github.com/CSIRO-enviro-informatics/pyldapi/',
    },
)
