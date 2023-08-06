from setuptools import setup

with open('README.rst', 'r') as infile:
    long_description = infile.read()

setup(name="shuttertalk",
      version="0.2",
      description="something",
      long_description=long_description,
      url="http://lav.io",
      author="Sam",
      author_email="lavigne@nyu.edu",
      license="GPL",
      packages=["shuttertalk"],
      scripts=["bin/shuttertalk"],
      install_requires=["bs4", "requests"])
