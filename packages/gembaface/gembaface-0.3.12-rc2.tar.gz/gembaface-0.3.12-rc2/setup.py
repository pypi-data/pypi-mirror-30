import os
from setuptools import setup


VERSION = '0.3.12-rc2'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='gembaface',
    version=VERSION,
    packages=['gembaface'],
    install_requires=[
        'requests',
        ]
    )
    
