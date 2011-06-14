import os
from jenkinsutils import BuildHelper

package = 'BlazeUtils'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

# install test requirements
print os.environ.get('PIP_INDEX_URL', None)
print os.environ.get('PIP_EXTRA_INDEX_URL', None)

bh.oscall('pwd')
bh.oscall('which', 'pip')
bh.pip_install_reqs('pip-jenkins-reqs.txt')

# install package w/ setuptools develop
bh.setuppy_develop()

# run tests & coverage
bh.vecall(
    'nosetests', 'tests', '--with-coverage',
    '--cover-package=blazeutils',
    '--with-xunit', '--with-xcoverage', '--cover-tests'
)
