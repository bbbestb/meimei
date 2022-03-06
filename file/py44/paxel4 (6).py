#!/usr/bin/python
# use Fabric to manage all the hosts in perf env.
# usage: fab -f vps_fabfile.py download_backup
# author: Jay <smile665@gmail.com>

from fabric.context_managers import cd
#from fabric.context_managers import settings
from fabric.operations import *
from fabric.api import *
from datetime import datetime

env.hosts = 'smilejay.com'
env.port = 22
env.user = 'root'
env.password = '1234'


@task
def put_sshkey():
    # add ssh public key of the master to remote slaves.
    with cd('/tmp'):
        put('id_rsa.pub.master', 'id_rsa.pub.master')
        put('add_sshkey.sh', 'add_sshkey.sh')
        run('bash add_sshkey.sh id_rsa.pub.master')


@task
def download_backup():
    # backup my WP file and database, download them to the local machine
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    local_dir = '/home/jay/backup'
    with cd('/tmp'):
        nginx = '/usr/share/nginx'
        wp_root = '/usr/share/nginx/html'
        exclude = 'html/wp-content/cache'
        bk_name = 'wp_%s.tar.gz' % dt
        clean = 'rm -f wp*.tar.gz'
        mysql = 'mysqldump -uroot -p1234 -A > %s/mysql-dump.sql' % wp_root
        tar = 'tar -zcf %s -C %s html --exclude=%s' % (bk_name, nginx, exclude)
        run(clean)
        run(mysql)
        run(tar)
        get(bk_name, '%s/%s' % (local_dir, bk_name))
