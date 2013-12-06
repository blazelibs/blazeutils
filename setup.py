import sys, os
import os.path as osp
try:
    from setuptools import setup, find_packages
    from setuptools.command.develop import develop as STDevelopCmd
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

class DevelopCmd(STDevelopCmd):
    def run(self):
        # add in requirements for testing only when using the develop command
        self.distribution.install_requires.extend([
            'mock',
            'nose',
            'xlwt',
            'xlrd',
            'docutils',
        ])
        STDevelopCmd.run(self)

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()
VERSION = open(os.path.join(cdir, 'blazeutils', 'version.txt')).read().strip()

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
    cmdclass = {'develop': DevelopCmd},
)
