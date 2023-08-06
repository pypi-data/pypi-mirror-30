#!/usr/bin/env python

from codecs import open
from os import path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from carillon import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the PROJECT file
with open(path.join(here, 'PROJECT.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Carillon',
    version=__version__,
    description='Ultra simple keyboard layout controller',
    long_description=long_description,
    url='https://github.com/sbreatnach/carillon',
    download_url = 'https://github.com/sbreatnach/carillon/archive/{}.tar.gz'.
        format(__version__),
    license='MIT',
    author='Shane Breatnach',
    author_email='shane.breatnach@gmail.com',
    packages=['carillon'],
    include_package_data=True,
    keywords='carillon setxkbmap keyboard keyboards layout linux openbox',
    install_requires=[
        'PyYAML>=3.12',
        'pygobject>=3.20',
        'six>=1.11.0'
    ],
    python_requires='~=3.3',
    entry_points={
        'console_scripts': [
            'carillon=carillon.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
