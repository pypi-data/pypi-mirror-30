# -*- coding:utf-8 -*-

from setuptools import setup
from setuptools import find_packages

VERSION = '1.0.1'

setup(
    name='awspycli',
    description='using python code to communicate with aws client',
    long_description='',
    classifiers=[],
    keywords='',
    author='Lawes',
    author_email='haiou_chen@sina.cn',
    url='https://github.com/MrLawes/awspycli',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'awscli==1.14.63',
    ],
    version=VERSION,
)
