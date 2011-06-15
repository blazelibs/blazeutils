import os
from jenkinsutils import BuildHelper

package = 'BlazeUtils'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

# install test requirements, use EI for coverage so we get pre-compiled version
# on windows
#
# version (have to do version 3.4 b/c nosexcover will fail with newer version)
# bug report for that: https://github.com/cmheisel/nose-xcover/issues/5
bh.vecall('easy_install', 'coverage==3.4')
bh.pip_install_reqs('pip-jenkins-reqs.txt')

# install package w/ setuptools develop
bh.setuppy_develop()

# run tests & coverage
bh.vecall(
    'nosetests', 'tests', '--with-xunit',
    '--with-coverage', '--cover-package=blazeutils', '--cover-tests',
    '--with-xcoverage',
)
