# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

test_requirements = []
required = [
    'Flask==0.12.2',
    'Flask-Bootstrap==3.3.7.1',
    'Flask-Script==2.0.5',
    'Flask-WTF==0.14.2',
    'pdfebc-core==0.2.0',
    'redis==2.10.5',
    'celery==4.0.2']

setup(
    name='pdfebc-web',
    version='0.1.0',
    description='Web interface for pdfebc.',
    long_description=readme,
    author='Simon Larsén',
    author_email='slarse@kth.se',
    url='https://github.com/slarse/pdfebc-web',
    download_url='https://github.com/slarse/pdfebc-web/archive/v0.1.0.tar.gz',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['bin/pdfebc-web', 'bin/pdfebc-web-start-celery-redis'],
    tests_require=test_requirements,
    install_requires=required
)
