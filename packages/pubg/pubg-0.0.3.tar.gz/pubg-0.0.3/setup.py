from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pubg',
    version='0.0.3',
    packages=['pubg'],
    url='https://github.com/nicolaskenner/python-pubg-api-wrapper',
    license='MIT',
    author='Nicolas Kenner',
    author_email='nick@nicolaskenner.com',
    description='Python wrapper for the Battlegrounds Developer API',
    long_description=long_description,
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ]
)
