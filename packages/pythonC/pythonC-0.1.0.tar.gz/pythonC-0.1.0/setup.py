#!usrbinenv python
#-- codingutf-8 --

#############################################
# File Name setup.py
# Author jack
# Created Time  2018-3-28
#############################################


from setuptools import setup, find_packages

setup(
    name = "pythonC",
    version = "0.1.0",
    keywords = ("pip", "hello"),
    description = "simple python",
    long_description = "simple python",
    license = "MIT Licence",

	url="https://github.com/jieji700/pythonC",
    author ="jack",
	author_email = "jiangjie-007@163.com",
	
    packages = find_packages(),
    include_package_data = True,
    platforms = "any"
)