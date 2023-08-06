#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@file:    setup.py
@time:    2018/4/10 14:53
"""


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='matlab-python',
    version='0.1.1',
    description='Call matlab from python',
    url='https://github.com/xbanke/matpy',
    author='quantpy',
    author_email='quantpy@gmail.com',
    license='MIT',
    packages=['matpy'],
    keywords=['matlab', 'python', 'matpy'],
    install_requires=['matpy', 'attrs', 'numpy'],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
