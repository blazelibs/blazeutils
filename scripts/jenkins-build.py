from jenkinsutils import BuildHelper

package = 'BlazeUtils'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

# install test requirements
bh.pip_install_reqs('pip-jenkins-reqs.txt')

# install package w/ setuptools develop
bh.setuppy_develop()

# run tests & coverage
bh.vecall(
    'nosetests', 'tests', '--with-coverage',
    '--cover-package=blazeutils',
    '--with-xunit', '--with-xcoverage', '--cover-tests'
)
