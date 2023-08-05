# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Email:  hhczy1003@163.com
# @Date:   2017-08-01 20:37:27
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-17 11:36:55

from setuptools import setup

setup(
    name="easyspider",
    version="1.3.1",
    author="yiTian.zhang",
    author_email="hhczy1003@163.com",
    packages=["easyspider"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "scrapy",
        "scrapy-redis",
        "pymongo",
        "apscheduler",
        "selenium",
    ],
    entry_points={
        "console_scripts": ["easyspider = easyspider.core.cmdline:execute"]
    }
)
