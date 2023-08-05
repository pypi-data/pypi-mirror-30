# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.0.4'


setup(
    name='pywe-pay-notify',
    version=version,
    keywords='Wechat Weixin Pay Notify',
    description='Wechat Pay Notify Module for Python.',
    long_description=open('README.rst').read(),

    url='https://github.com/sdkwe/pywe-pay-notify',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['pywe_pay_notify'],
    py_modules=[],
    install_requires=['pywe_sign', 'pywe_xml'],

    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
