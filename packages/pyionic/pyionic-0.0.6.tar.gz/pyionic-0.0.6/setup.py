# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

requires = [
    'requests>=2.18.4'
]

setup(
    name='pyionic',
    version='0.0.6',
    description='Python package for the Ion Channel API',
    long_description=readme,
    author='Patrick Pierson',
    author_email='patrick.pierson@ionchannel.io',
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=requires,
    url='https://github.com/ion-channel/pyionic',
    license='BSD',
    packages=find_packages(exclude=('tests', 'docs'))
)
