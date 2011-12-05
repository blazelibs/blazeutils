import os
from jenkinsutils import BuildHelper

package = 'BlazeUtils'
type = 'build'

bh = BuildHelper(package, type)

# delete & re-create the venv
bh.venv_create()

# use easy_install for coverage so we get pre-compiled version on windows
bh.vepycall('easy_install', 'coverage')

# have to install dev build of mock using pip directly because of pip bug:
# https://github.com/pypa/pip/issues/145
bh.vepycall('pip', 'install', 'http://www.voidspace.org.uk/downloads/mock-0.8.0beta4.tar.gz#egg=mock-dev')

# install other jenkins requirements
bh.pip_install_reqs('pip-jenkins-reqs.txt')

# install package w/ setuptools develop
bh.setuppy_develop()

# run tests & coverage
bh.vepycall(
    'nosetests', 'tests', '--with-xunit',
    '--with-xcoverage', '--cover-package=blazeutils', '--cover-tests',

)
