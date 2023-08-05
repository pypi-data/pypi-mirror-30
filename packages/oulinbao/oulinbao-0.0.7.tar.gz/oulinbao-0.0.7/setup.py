from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='oulinbao',
    version='0.0.7',
    description='oulinbao test pypi',
    long_description=long_description,
    author='oulinbao',
    url='https://pypi.org/project/oulinbao/',
    scripts=[],
    packages=find_packages(),
    install_requires=[],

    classifiers=[  # Optional
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

)
