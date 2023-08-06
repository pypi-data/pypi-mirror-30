from setuptools import setup

setup(name="slidepull",
    version="0.1",
    description="something",
    url="http://alden.life",
    author="Alden",
    author_email="rivendalejones@gmail.com",
    license="GPL",
    packages=["shuttertalk"],
    scripts=["bin/shuttertalk"],
    install_requires=["bs4", "requests"])
