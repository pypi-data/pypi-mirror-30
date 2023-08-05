from fabric.api import *


class supervisor:

    @staticmethod
    def install():
        run('sudo apt-get -y install supervisor')

    @staticmethod
    def enable():
        run('sudo systemctl enable supervisor')

    @staticmethod
    def start():
        run('sudo systemctl start supervisor')