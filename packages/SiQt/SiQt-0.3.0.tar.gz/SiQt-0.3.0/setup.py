# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from SiQt._version import __version__


with open('README.rst', 'r') as fh:
    long_description = fh.read()


setup(name='SiQt',
      version=__version__,
      description='Convenience tools for building PyQt/PySide '
                  'based GUI applications.',
      author='Roman Yurchak',
      author_email='rth.yurchak@gmail.com',
      url='https://github.com/symerio/SiQt',
      license='MIT',
      packages=find_packages(),
      install_requires=['qtpy'],
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          ])
