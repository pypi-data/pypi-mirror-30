# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='pyspedas',
    version='0.2.2',
    description='Package for SPEDAS data loading modules',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/nickssl/pyspedas',
    author='Nick Hatzigeorgiu',
    author_email='nikos@berkeley.edu',
    license='MIT',
    classifiers=['Development Status :: 3 - Alpha', 
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',
    ],
    keywords='spedas data tools',
    project_urls={'Information': 'http://spedas.org/wiki/',
                 },    
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),          
    install_requires=['pytplot'],
    python_requires='>=3',
)

