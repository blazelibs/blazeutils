#!/bin/bash

MYDIR="$( cd "$( dirname "$0" )" && pwd )"

SRCDIR="$MYDIR/.."
ROOTDIR="$MYDIR/../.."
VENVDIR="$ROOTDIR/blazeutils-hudson-venv"

cd $SRCDIR
hg pull -u

# setup a virtualenv
rm -rf $VENVDIR
virtualenv --no-site-packages "$VENVDIR"

# activate virtualenv
source "$VENVDIR/bin/activate"

# install blazeutils
python setup.py install
