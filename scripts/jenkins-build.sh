PKGNAME="BlazeUtils"
VENVDIR="$WORKSPACE/.venv"

cd $WORKSPACE

# setup a virtualenv
if [ -d ".venv" ]; then
    echo "**> virtualenv exists"
else
    echo "**> creating virtualenv"
    virtualenv "$VENVDIR" --no-site-packages -q
fi

# activate virtualenv
source "$VENVDIR/bin/activate"

# install test requirements
pip install -r requirements-testing.txt

# install package
python setup.py develop

# install as dev package
python setup.py --quiet develop

# run tests
nosetests tests --with-coverage --cover-package=blazeutils --with-xunit --with-xcoverage --cover-tests
