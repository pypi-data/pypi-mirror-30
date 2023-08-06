from setuptools import setup, find_packages
from os.path import join, dirname
import testbot

setup(
    name='testbot',
    version=testbot.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'telepot==12.5',
        'pillow==5.0.0',
        'pandas==0.22.0',
        'motor==1.2.1',
        'matplotlib',
        'aiohttp',
        'numpy'
    ],
    url='https://github.com/antonsluch/economics-bot/',
    author='Anton Sluch',
    author_email='asluch@nes.ru'
)
