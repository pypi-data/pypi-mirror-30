#!/usr/bin python
# coding: utf-8

from setuptools import setup

setup(
    name='fuckpip',
    version='0.0.1',
    author='2627866800',
    author_email='2627866800@qq.com',
    url='https://zhuanlan.zhihu.com/p/26159930',
    description=u'测试pip安装包',
    packages=['fuckpip'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'fuck=fuckpip.test:fuck',
            'love=fuckpip.test:love'
        ]
    }
)