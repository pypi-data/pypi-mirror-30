from setuptools import setup

setup(name="dtwNonsense", 
      version="0.1", 
      description="something",
      url="http://jhjameshuang.com",
      author="James",
      author_email="jjh568@nyu.edu",
      license="GPL",
      packages=["shuttertalk"], # this should be exactly the name of the package folder
      scripts=["bin/shuttertalk"],
      install_requires=["bs4", "requests"])