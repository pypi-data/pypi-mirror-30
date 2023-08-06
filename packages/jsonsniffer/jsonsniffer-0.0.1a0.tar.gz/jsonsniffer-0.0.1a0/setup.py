# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


version = __import__('jsonsniffer').__version__


setup(
    name = 'jsonsniffer',
    packages = find_packages(),
    version = version,
    description = ('A simple library for parsing complex json data to and '
                   'from Python datatypes'),
    author = 'Angelchev Artem',
    author_email = 'artangelchev@gmail.com',
    url = 'https://github.com/ArtemAngelchev/JsonSniffer.git',
    keywords = ['serialization', 'deserialization', 'json', 'schema', 'validation'], # arbitrary keywords
    install_requires=['jmespath'],
    license='MIT',
    classifiers = [
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
