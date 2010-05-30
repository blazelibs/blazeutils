"""
Introduction
---------------

pysutils is a library to hold common tools for the pys* library family:

- `pysmvt <http://pypi.python.org/pypi/pysmvt/>`_
- `pysapp <http://pypi.python.org/pypi/pysapp/>`_
- `pysform <http://pypi.python.org/pypi/pysform/>`_

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/pyslibs

Current Status
---------------

The code stays pretty stable, but the API is likely to change in the future.

The `pysutils tip <http://bitbucket.org/rsyring/pysutils/get/tip.zip#egg=pysutils-dev>`_
is installable via `easy_install` with ``easy_install pysutils==dev``
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.2'

setup(
    name = "pysutils",
    version = version,
    description = "A collection of python utility functions and classes.",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://pypi.python.org/pypi/pysutils/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=['pysutils']
)