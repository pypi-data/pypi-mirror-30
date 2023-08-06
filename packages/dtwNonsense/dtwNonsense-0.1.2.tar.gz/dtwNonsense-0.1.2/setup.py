from setuptools import setup

with open("README.rst", 'r') as infile:
    long_description = infile.read()

setup(name="dtwNonsense", 
      version="0.1.2", 
      description="something",
      long_description=long_description,
      url="http://jhjameshuang.com",
      author="James",
      author_email="jjh568@nyu.edu",
      license="GPL",
      packages=["shuttertalk"], # this should be exactly the name of the package folder
      scripts=["bin/shuttertalk"],
      install_requires=["bs4", "requests"])