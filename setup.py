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

The code for 0.1 is pretty stable.  API, however, will be changing in 0.2.

The mostly stable `development version
<https://svn.rcslocal.com:8443/svn/pysmvt/pysutils/trunk#egg=pysutils-dev>`_.
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = "pysutils",
    version = "0.1",
    description = "A collection of python utility functions and classes.",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://pypi.python.org/pypi/pysutils/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    py_modules=['pysutils']
)