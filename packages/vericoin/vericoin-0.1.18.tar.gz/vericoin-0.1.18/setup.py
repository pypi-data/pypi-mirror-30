# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='vericoin',
    version='0.1.18',
    packages=[
        'vericoin',
        'vericoin.core'
    ],
    install_requires=[
        'requests',
        'pandas',
        'ratelimit'
    ],
    url='https://github.com/sharebook-kr/vericoin',
    author='jonghun.yoo',
    author_email='jonghun.yoo@outlook.com',
    description='암호화폐 Daily 가격 조회',
)
