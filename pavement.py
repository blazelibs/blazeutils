"""
Introduction
---------------

BlazeUtils is a library to hold common tools for the Blaze library family:

- `BlazeWeb <http://pypi.python.org/pypi/BlazeWeb/>`_
- `BaseBWA <http://pypi.python.org/pypi/BaseBWA/>`_
- `BlazeForm <http://pypi.python.org/pypi/BlazeForm/>`_

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

The code and API stay pretty stable.

The `blazeutils tip <http://bitbucket.org/rsyring/blazeutils/get/tip.zip#egg=blazeutils-dev>`_
is installable via `easy_install` with ``easy_install blazeutils==dev``
"""
from paver.easy import *
import paver.doctools
from paver.setuputils import setup

setup(
    name = "BlazeUtils",
    version = '0.3.3',
    description = "A collection of python utility functions and classes.",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://bitbucket.org/rsyring/blazeutils/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=['blazeutils']
)

@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
