from fabric.api import *


class git:
    @staticmethod
    def clone(link):
        run('git clone {}'.format(link))