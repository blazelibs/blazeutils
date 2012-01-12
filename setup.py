import sys, os
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from blazeutils import VERSION

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

setup(
    name = "BlazeUtils",
    version = VERSION,
    description = "A collection of python utility functions and classes.",
    long_description= '\n\n'.join((README, CHANGELOG)),
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://bitbucket.org/rsyring/blazeutils/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
      ],
    license='BSD',
    packages=['blazeutils'],
    zip_safe=False,
)
