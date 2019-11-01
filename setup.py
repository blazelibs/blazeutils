import os.path as osp

from setuptools import setup


cdir = osp.abspath(osp.dirname(__file__))
with open(osp.join(cdir, 'readme.rst')) as fp:
    README = fp.read()
with open(osp.join(cdir, 'changelog.rst')) as fp:
    CHANGELOG = fp.read()

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
    author_email="randy.syring@level12.io",
    url='https://github.com/blazelibs/blazeutils/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3',
    license='BSD',
    packages=['blazeutils'],
    zip_safe=False,
    include_package_data=True,
    install_requires=['six', 'wrapt'],
)
