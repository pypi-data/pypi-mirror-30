# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


requires = [
    'requests>=2.18.4'
]

setup(
    name='pyionic',
    version='0.0.1',
    description='Python package for the Ion Channel API',
    long_description=readme,
    author='Patrick Pierson',
    author_email='patrick.pierson@ionchannel.io',
    install_requires=requires,
    url='https://github.com/ion-channel/pyionic',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
