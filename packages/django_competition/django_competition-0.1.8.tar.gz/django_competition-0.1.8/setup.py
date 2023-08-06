# coding=utf-8

from setuptools import find_packages, setup
import pathlib
import os
from pip.req import parse_requirements
from pip.download import PipSession

MAIN_DIR = pathlib.Path(__file__).absolute().parent


def get_requirements():
  pip_session = PipSession()
  return parse_requirements(
      str(MAIN_DIR / 'requirements' / 'base.in'),
      session=pip_session
  )

packages = find_packages(
  str(MAIN_DIR),
  include=('django_competition',),
  exclude=[]
)

if __name__ == "__main__":

  setup(
    name='django_competition',
    version='0.1.8',
    packages=packages,
    license='Apache',
    author='Jacek Bzdak',
    author_email='jacek@askesis.pl',
    description='Simple vote mechanism for a competition',
    install_requires=[
      "Django",
      "Markdown",
      "mailchecker",
      "bleach",
    ],
    include_package_data=True
  )
