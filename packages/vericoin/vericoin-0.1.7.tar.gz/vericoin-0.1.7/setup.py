# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='vericoin',
    version='0.1.7',
    packages=find_packages(include=['vericoin/core']),
    install_requires=['pandas', 'ratelimit'],
    url='https://github.com/sharebook-kr/vericoin',
    author='jonghun.yoo',
    author_email='jonghun.yoo@outlook.com',
    description='암호화폐 Daily 가격 조회',
)