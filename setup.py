"""
Introduction
---------------

BlazeUtils is a library to hold common tools for the Blaze library family:

- `pysmvt <http://pypi.python.org/pypi/BlazeWeb/>`_
- `pysapp <http://pypi.python.org/pypi/TioBWA/>`_
- `pysform <http://pypi.python.org/pypi/BlazeForm/>`_

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/pyslibs

Current Status
---------------

The code stays pretty stable, but the API is likely to change in the future.

The `blazeutils tip <http://bitbucket.org/rsyring/blazeutils/get/tip.zip#egg=blazeutils-dev>`_
is installable via `easy_install` with ``easy_install blazeutils==dev``
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from blazeutils import VERSION

setup(
    name = "BlazeUtils",
    version = VERSION,
    description = "A collection of python utility functions and classes.",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://pypi.python.org/pypi/blazeutils/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=['blazeutils']
)
