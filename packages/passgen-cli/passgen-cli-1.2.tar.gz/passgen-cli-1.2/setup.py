# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
from setuptools import setup
 
version = "1.2"
descr = "This is simple CLI random password generator. It combines punctuations, letters (upper and lower cases) and digits.\n\n"
descr += "Installation:\n `pip install passgen-cli`\n\n"
descr += "Options:\n `-l INTEGER  length of the password.`\n\n"
descr += "Without the `-l` option, it returns 12 characters by default.\n\nExample: `passgen-cli -l 13`\n\n"

def readme():
    with open("README.rst") as f:
        return f.read() 

 
setup(
    name = "passgen-cli",
    packages = ["passgen-cli"],
    version = version,
    description = "Python command line password generator.",
    long_description = descr,
    author = "Colby Alladaye",
    keyword= "password generator",
    author_email = "colbyter@gmail.com",
    url = "https://github.com/Colbyter/passgen-cli",
    install_requires=['click'],
    license='MIT',
     entry_points = {
        'console_scripts': ['passgen-cli=passgen_cli:main'],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
],
    )