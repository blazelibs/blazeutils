#!/bin/bash

MYDIR="$( cd "$( dirname "$0" )" && pwd )"

PKGNAME="BlazeUtils"
SRCDIR="$MYDIR/.."
ROOTDIR="$MYDIR/../.."
VENVDIR="$ROOTDIR/hudson-venv"

cd $SRCDIR
hg pull -u

# setup a virtualenv
rm -rf $VENVDIR
virtualenv --no-site-packages "$VENVDIR"

# activate virtualenv
source "$VENVDIR/bin/activate"

# install package
python setup.py install

# uninstall blazeutils from venv
pip uninstall -y "$PKGNAME"

# install as dev package
python setup.py develop

# run tests
nosetests tests
