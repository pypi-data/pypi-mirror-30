#coding:utf-8

from os import path
from codecs import open
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'winney',
    version = '0.1.0',
    author = 'olivetree123',
    license = 'BSD',
    packages = ['winney'],
    author_email = 'olivetree123@163.com',
    url = 'https://github.com/olivetree123/Winny',
    description = 'Object-Oriented HTTP Request',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = [
        "requests>=2.18.0",
    ],
)