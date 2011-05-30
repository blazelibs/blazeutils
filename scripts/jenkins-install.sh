PKGNAME="BlazeUtils"
VENVDIR="$WORKSPACE/.venv-install"

cd $WORKSPACE

# remove the install venv so we start from scratch
rm -rf "$VENVDIR"

# create a new virtualenv
virtualenv "$VENVDIR" --no-site-packages -q

# activate virtualenv
source "$VENVDIR/bin/activate"

# install from pypi
pip install "$PKGNAME"

# import it
python -c 'import blazeweb'
