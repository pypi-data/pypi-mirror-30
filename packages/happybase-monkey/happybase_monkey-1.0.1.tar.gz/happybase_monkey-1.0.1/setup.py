# coding:utf-8
__author__ = 'qinman'
# create by qinman on 2018/4/13

from setuptools import setup, find_packages

setup(
    name='happybase_monkey',
    version='1.0.1',
    description=(
        '<向 hbase put 数据时，自动建立索引表并向索引表中插入数据>'
    ),
    author='applepie',
    author_email='1961356350@qq.com',
    packages=find_packages(),
    install_requires=['happybase']
)