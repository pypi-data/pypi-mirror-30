# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "bdz_util",
    version = "0.0.3",
    keywords = ("pip", "util", "bdz_util", "httpclient"),
    description = "常用工具类",
    long_description = "可以上天的常用工具类",
    license = "MIT Licence",

    url = "http://www.www.www.",
    author = "chenjian",
    author_email = "goudanbaba123@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests"]
)

if __name__ == "__main__":
    pass