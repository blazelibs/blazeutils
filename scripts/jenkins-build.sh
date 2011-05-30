PKGNAME="BlazeUtils"
VENVDIR="$WORKSPACE/.venv-dev"

cd $WORKSPACE

# setup a virtualenv
if [ -d "$VENVDIR" ]; then
    echo "**> virtualenv exists"
else
    echo "**> creating virtualenv"
    virtualenv "$VENVDIR" --no-site-packages -q
fi

# activate virtualenv
source "$VENVDIR/bin/activate"

# install test requirements
pip install -r requirements-testing.txt

# install as dev package
python setup.py --quiet develop

# run tests
nosetests tests --with-coverage --cover-package=blazeutils --with-xunit --with-xcoverage --cover-tests
