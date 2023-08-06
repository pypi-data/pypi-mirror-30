from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name="slidepull",
    version="0.11",
    description="something",
    url="http://alden.life",
    author="Alden",
    author_email="rivendalejones@gmail.com",
    license="GPL",
    packages=["shuttertalk"],
    scripts=["bin/shuttertalk"],
    install_requires=["bs4", "requests"])
