""" A setuptools based setup module.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
try:
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

setup(
    name = 'nemwriter',
    packages = ['nemwriter'],
    version = '0.1.1',
    description = 'Write meter readings to AEMO NEM12 (interval metering data) and NEM13 (accumulated metering data) data files ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = 'aguinane',
    author_email = 'alexguinane@gmail.com',
    url = 'https://github.com/aguinane/nem-writer',
    keywords = ['energy', 'NEM12', 'NEM12'],
    classifiers = [],
    license = 'MIT',
)
