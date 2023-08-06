#!/usr/bin/env python
# coding=utf-8


from setuptools import setup, find_packages

setup(
    author="chenjiandongx",
    author_email="chenjiandongx@qq.com",
    name="lolly",
    version="0.1.0",
    license="MIT",
    url="https://github.com/chenjiandongx/lolly",
    install_requires=["click", "pillow"],
    py_modules=["lolly"],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    description="Generate words gif image via the command line",
    entry_points={"console_scripts": ["lolly=lolly:command_line_runner"]},
)
