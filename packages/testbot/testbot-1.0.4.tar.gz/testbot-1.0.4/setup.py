# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os.path import join, dirname
import testbot

setup(
    name='testbot',
    version=testbot.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'telepot',
        'pillow',
        'pandas',
        'motor',
        'matplotlib',
    ],
    url='https://github.com/antonsluch/economics-bot/',
    author='Anton Sluch',
    author_email='asluch@nes.ru'
)
