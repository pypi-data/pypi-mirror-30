# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "rule_spider",
    version = "0.0.1",
    keywords = ("pip", "util", "bdz_util", "httpclient","spider","rule"),
    description = "常用工具类",
    long_description = "可以上天的常用工具类",
    license = "MIT Licence",

    url = "http://github.com/badaozhai",
    author = "chenjian",
    author_email = "goudanbaba123@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests","flask"]
)

if __name__ == "__main__":
    pass