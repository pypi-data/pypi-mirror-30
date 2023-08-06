from setuptools import setup

setup(name="shuttertalk",
      version="0.1",
      description="something",
      url="http://lav.io",
      author="Sam",
      author_email="lavigne@nyu.edu",
      license="GPL",
      packages=["shuttertalk"],
      scripts=["bin/shuttertalk"],
      install_requires=["bs4", "requests"])
