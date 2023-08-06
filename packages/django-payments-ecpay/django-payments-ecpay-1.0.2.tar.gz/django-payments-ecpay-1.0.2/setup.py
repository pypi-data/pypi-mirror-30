#!/usr/bin/env python
import sys

# Fix encoding problem on Legacy Python.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


setup(
    name='django-payments-ecpay',
    packages=['payments_ecpay'],
    version='1.0.2',
    description='A django-payments backend for the ECPay (Taiwan) payment gateway.',
    long_description=read_md('README.md'),
    author='Benjamin Xenos',
    author_email='benjamin@tornerdo.com',
    license='MIT',
    url='https://github.com/tornerdo/django-payments-ecpay',
    download_url='https://github.com/tornerdo/django-payments-ecpay/archive/v1.0.tar.gz',
    keywords=['django-payments', 'payment gateway'],
    classifiers=[],
)
