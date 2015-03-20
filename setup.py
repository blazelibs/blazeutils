import os.path as osp
import sys

from setuptools import setup


PY2 = sys.version_info[0] == 2

# pip install -e .[develop]
develop_requires = [
    'mock',
    'pytest',
    'pytest-cov',
    'xlrd',
    'docutils',
    'sqlalchemy',
]

if PY2:
    develop_requires.append('xlwt')


cdir = osp.abspath(osp.dirname(__file__))
README = open(osp.join(cdir, 'readme.rst')).read()
CHANGELOG = open(osp.join(cdir, 'changelog.rst')).read()

version_fpath = osp.join(cdir, 'blazeutils', 'version.py')
version_globals = {}
with open(version_fpath) as fo:
    exec(fo.read(), version_globals)

setup(
    name="BlazeUtils",
    version=version_globals['VERSION'],
    description="A collection of python utility functions and classes.",
    long_description='\n\n'.join((README, CHANGELOG)),
    author="Randy Syring",
    author_email="randy@thesyrings.us",
    url='http://bitbucket.org/blazelibs/blazeutils/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    license='BSD',
    packages=['blazeutils'],
    extras_require={'develop': develop_requires},
    zip_safe=False,
    include_package_data=True,
    install_requires=['six', 'wrapt'],
)
