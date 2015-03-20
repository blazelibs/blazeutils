import os
from jenkinsutils import BuildHelper

package = 'BlazeUtils'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

# use easy_install for coverage so we get pre-compiled version on windows
bh.vepycall('easy_install', 'coverage')

# install other jenkins requirements
bh.pip_install_reqs('pip-jenkins-reqs.txt')

# install package w/ setuptools develop
bh.setuppy_develop()

# run tests & coverage
bh.vepycall(
    'nosetests', 'tests', '--with-xunit',
    '--with-xcoverage', '--cover-package=blazeutils', '--cover-tests',

)
