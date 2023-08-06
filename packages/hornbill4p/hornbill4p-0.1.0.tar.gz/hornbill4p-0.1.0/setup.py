# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='hornbill4p',
    version='0.1.0',
    description='hornbill python client and util',
    long_description=readme,
    author='mouhao',
    author_email='mouhao@hudongpai.com',
    url='http://www.datastory.com.cn',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
