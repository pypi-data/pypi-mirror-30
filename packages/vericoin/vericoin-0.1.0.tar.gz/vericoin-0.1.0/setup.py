# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README') as f:
    readme = f.read()

setup(
    name='vericoin',
    version='0.1.0',
    description='암호화폐 Daily 가격 조회',
    long_description=readme,
    author='jonghun.yoo',
    author_email='jonghun.yoo@outlook.com',
    url='https://github.com/sharebook-kr/vericoin',
    keywords='coin cryptocurrency',
    license='GPL',
    packages=find_packages(exclude=[]),
)

