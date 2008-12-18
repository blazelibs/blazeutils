"""
Introduction
---------------

pysutils is a library to hold common tools for the pys* library family:

- `pysmvt <http://pypi.python.org/pypi/pysmvt/>`_
- `pysapp <http://pypi.python.org/pypi/pysapp/>`_
- `pysform <http://pypi.python.org/pypi/pysform/>`_

Current Status
---------------

We are currently in an alpha phase which means lots of stuff can change, maybe rapidly, and we are not interested in backwards compatibility at this point.

I am currently using this library for some production websites, but I wouldn't recommend you do that unless you **really** know what you are doing.

The unstable `development version
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
    version = "0.1dev",
    description = "A collection of python utility functions and classes.",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://pypi.python.org/pypi/pysutils/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    py_modules=['pysutils']
)