# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list).
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

import logging
logging.basicConfig(level=logging.DEBUG)

from six.moves import configparser

from fabric.api import local
from fabric.api import task
from fabric.api import run
from fabric.api import env
from fabric.tasks import Task

config = configparser.ConfigParser({
    'remote': 'origin',
    'branch': 'master',
    'uwsgi-emperor': 'xmpp-server-list',
})
config.read('fab.conf')


@task
def test():
    folders = 'account api bootstrapform confirm core server xmpp xmpplist'
    local('isort --check-only --diff -rc %s' % folders)
    local('flake8 %s' % folders)
    local('python -Wd manage.py check')
    local('python manage.py test')


@task
def update(section='DEFAULT'):
    """Update a local installation."""

    uwsgi_emperor = config.get(section, 'uwsgi-emperor')
    local('git pull origin master')
    local('python manage.py migrate')
    local('touch /etc/uwsgi-emperor/vassals/%s.ini' % uwsgi_emperor)


class DeployTask(Task):
    def run(self, section='DEFAULT'):
        host = config.get(section, 'host')
        remote = config.get(section, 'remote')
        branch = config.get(section, 'branch')
        group = config.get(section, 'group')
        path = config.get(section, 'path')

        local('git push %s %s' % (remote, branch))
        ssh = lambda cmd: local('ssh %s sudo sg %s -c \'"cd %s && %s"\'' % (host, group, path, cmd))
        manage = lambda cmd: ssh('../bin/python manage.py %s' % cmd)
        local('ssh %s sudo chgrp -R %s %s' % (host, group, path))
        ssh("git fetch")
        ssh("git pull origin master")
        ssh("../bin/pip install -r requirements.txt")
        manage('migrate')
        manage('collectstatic --noinput')
        manage('geoip')
        ssh("touch /etc/uwsgi-emperor/vassals/%s.ini" % uwsgi_emperor)


#deploy = DeployTask()
