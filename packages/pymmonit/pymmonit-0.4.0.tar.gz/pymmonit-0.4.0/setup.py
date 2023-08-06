import sys

from setuptools import find_packages, setup


exec(open('pymmonit/_version.py').read())

_extras = {
    'test': [
        'pytest>=3.1',
        'pytest-mock',
    ]
}

setup(name='pymmonit',
      version=__version__,
      description='MMonit API wrapper written in Python',
      author='Jon Thacker',
      author_email='thacker.jon@gmail.com',
      url='https://github.com/jthacker/PyMMonit',
      license='GPLv3',
      packages=find_packages(),
      extras_require=_extras,
      tests_require=_extras['test'],
      install_requires=['requests >= 2.18.0'])
