from distutils.core import setup
from setuptools import find_packages

setup(
    name='packer.py',
    version='0.0.1.dev0',
    author='Matthew Aynalem',
    author_email='maynalem@gmail.com',
    packages=find_packages('packer'),
    package_dir={'': 'packer'},
    url='https://github.com/mayn/packer.py',
    description='packer.py - python wrapper for hashicorp packer',
    keywords="hashicorp packer",
    long_description=open('README.rst').read(),
    install_requires=[
    ],
)
