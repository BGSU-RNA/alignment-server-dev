from __future__ import with_statement

from fabric.api import task
from fabric.api import run
from fabric.api import local
from fabric.api import cd
from fabric.api import env
from fabric.api import prefix


env.hosts = ["api@rna.bgsu.edu"]
env.virtualenv = "api"
env.branch = 'develop'
env.deploy = "~/apps/alignments"


def common():
    env.app = env.deploy + "/app"


@task
def stop():
    common()
    with cd(env.app):
        with prefix("workon %s" % env.virtualenv):
            run("wsgid stop --app-path=%s" % env.deploy)


@task
def prod():
    env.branch = 'master'


@task
def merge():
    local("git checkout master")
    local("git merge master develop")


@task
def deploy():
    common()

#    local("git push origin %s" % env.branch)

    with cd(env.app):
        with prefix("workon %s" % env.virtualenv):
            run("git pull origin %s" % env.branch)
            run("wsgid restart --app-path=%s" % env.deploy)
