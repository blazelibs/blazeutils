import os
from jenkinsutils import BuildHelper

package = 'BlazeUtils'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

# use easy_install for coverage so we get pre-compiled version on windows
#
# Also, have to do version 3.4 b/c nosexcover will fail with newer version)
# bug report for that: https://github.com/cmheisel/nose-xcover/issues/5
bh.vepycall('easy_install', 'coverage==3.4')

# install other jenkins requirements
bh.pip_install_reqs('pip-jenkins-reqs.txt')

# install package w/ setuptools develop
bh.setuppy_develop()

# run tests & coverage
bh.vepycall(
    'nosetests', 'tests', '--with-xunit',
    '--with-xcoverage', '--cover-package=blazeutils', '--cover-tests',

)
