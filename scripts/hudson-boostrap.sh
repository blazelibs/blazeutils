#!/bin/bash
#rm -rf blazeutils-hudson-root
#mkdir -p blazeutils-hudson-root/src
#hg clone ssh://hg@bitbucket.org/rsyring/blazeutils blazeutils-hudson-root/src
#cd blazeutils-hudson-root/src
#paver hudson-test

MYDIR="$( cd "$( dirname "$0" )" && pwd )"

cd $MYDIR/..

# update source
hg pull -u

# remove the virtualenv
