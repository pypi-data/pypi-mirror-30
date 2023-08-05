from fabric.api import *


class nginx:

    @staticmethod
    def install():
        run('sudo apt-get -y install nginx')
