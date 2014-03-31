#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.colors import green, red
from fabric.contrib.console import confirm
from fabric.api import run, env, cd, put, sudo, abort

# configs
env.user = 'group'
env.hosts = ['210.44.176.241:2722',]
## project home path
PROJECT_HOME = '/home/group/gotit'
## project name in supervisor
PROJECT_NAME_IN_SUPERVISOR = 'gotit'
## default deploy branch
DEPLOY_BARNCH = 'zhwei'

def put_sshkey():
    """push ssh key to server
    """
    with cd('/tmp'):
        put('id_rsa.pub.master', 'id_rsa.pub.master')
        run('cat id_rsa.pub.master >> ~/.ssh/authorized_keys')

# git

def git_pull(branch):

    ret = run('git pull origin %s' % branch)
    if ret.failed and not confirm('Pull from origin %s Failed, Continue anyway ?') % branch:
        run('git status')
        abort(red('Aborting at pull from origin'))
    print(green('Pull from branch %s successfully') % branch)

# service control

def restart_project(project_name):

    #if not confirm(green('Do you want to restart project ?')):
    sudo('supervisorctl restart %s' % project_name)
    print(green('Restart Supervisor project [%s] Successfully !!') % project_name)

def restart_nginx(action="reload"):

    sudo('nginx -s %s' % action)
    print(green('[%s] Nginx Successfully !!') % action)

# python

def install_require(package=None):
    if package:
        sudo('pip install %s' % package)
    else:
        sudo('pip install -r requirements.txt')
    print(green('Install Complete !'))

# project custom

def deploy(do='app'):

    with cd(PROJECT_HOME):

        git_pull(DEPLOY_BARNCH)
        install_require()

        restart_project(PROJECT_NAME_IN_SUPERVISOR)
