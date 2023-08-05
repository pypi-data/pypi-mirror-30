from fabric.api import *


class Venv:
    @staticmethod
    def install(self):
        run('wget https://bootstrap.pypa.io/get-pip.py')
        run('sudo python3.6 get-pip.py')
        run('sudo pip3.6 install virtualenv')

    @staticmethod
    def start(venv, python_version='python3.6'):
        run('virtualenv {venv} -p {python_version}'.format(
            venv=venv,
            python_version=python_version
        ))

    @staticmethod
    def initialize(path_to_venv):
        """
        Use this to run commands in the specified venv using the WITH
        """
        with cd(path_to_venv):
            with prefix('source {}/bin/activate'.format(path_to_venv)):
                yield
