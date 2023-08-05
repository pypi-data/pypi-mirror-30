from fabric.api import *


class user:

    @staticmethod
    def add(user):
        run('adduser {}'.format(user))

    @staticmethod
    def grant_sudo(user):
        run('gpasswd -a {} sudo'.format(user))