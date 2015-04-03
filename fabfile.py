from __future__ import with_statement

from fabric.api import task
from fabric.api import run
from fabric.api import local
from fabric.api import cd
from fabric.api import env
from fabric.api import prefix


env.hosts = ["api@rna.bgsu.edu"]
env.virtualenv = "api"
env.base = '~/deploy'

# Differ between prod and dev
env.app_name = 'r3d-2-msa-dev'
env.branch = 'develop'


def common():
    env.app = '%s/apps/%s' % (env.base, env.app_name)


@task
def prod():
    env.app_name = 'r3d-2-msa'
    env.branch = 'master'


@task
def merge():
    local("git checkout master")
    local("git merge master develop")


@task
def update_options():
    with prefix("workon %s" % env.virtualenv):
        with cd(env.app):
            run("python bin/options.py --config conf/config.json")


@task
def deploy():
    common()

    with prefix("workon %s" % env.virtualenv):
        with cd(env.app):
            run("git pull origin %s" % env.branch)
            run("python bin/options.py --config conf/config.json")

        with cd(env.base):
            run("supervisorctl -c conf/supervisord.conf restart %s:*" %
                env.app_name)


@task
def status():
    with cd(env.base):
            run("supervisorctl -c conf/supervisord.conf status %s:*" %
                env.app_name)
