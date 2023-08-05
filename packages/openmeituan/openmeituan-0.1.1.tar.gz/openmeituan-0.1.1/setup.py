from setuptools import setup, find_packages

setup(
    name="openmeituan",
    version="0.1.1",
    description="an implementation of meituan open platform's APIs",
    url="https://github.com/farseer810/openmeituan",
    keywords="meituan meituan pay library",
    author="farseer810",
    author_email="farseer810@qq.com",
    license="MIT",
    packages=find_packages(),
    install_requires=['requests', 'six'],
    zip_safe=False)