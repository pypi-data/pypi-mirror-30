# -*- coding: utf-8 -*-
# Created by lijian on 2017/9/1.

from setuptools import setup, find_packages

setup(
    name="dqa_commonlib",
    version="0.3.3",
    url="https://github.com/xiaoyaoyuyi/python_package_test",
    description="common script operations liabray about python",
    author="xiaoyaoyuyi",
    author_email="389105015@qq.com",
    license="MIT",
    packages=find_packages(),
    classifiers=['Programming Language :: Python :: 2.7'],
    python_requires='>=2.7',
    install_requires=['MySQL-python'],
    package_data={
        'dqa_commonlib': ['setup.cfg', 'LICENSE.txt', 'MANIFEST.in'] 
    },
    keywords="dada qa commonlib",
)
