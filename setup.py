import os.path as osp
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

# pip install -e .[develop]
develop_requires = [
    'mock',
    'nose',
    'xlwt',
    'xlrd',
    'docutils',
    'sqlalchemy',
]


cdir = osp.abspath(osp.dirname(__file__))
README = open(osp.join(cdir, 'readme.rst')).read()
CHANGELOG = open(osp.join(cdir, 'changelog.rst')).read()

version_globals = {}
execfile(osp.join(cdir, 'blazeutils', 'version.py'), version_globals)

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
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    license='BSD',
    packages=['blazeutils'],
    extras_require={'develop': develop_requires},
    zip_safe=False,
    include_package_data=True,
    install_requires=['wrapt'],
)
