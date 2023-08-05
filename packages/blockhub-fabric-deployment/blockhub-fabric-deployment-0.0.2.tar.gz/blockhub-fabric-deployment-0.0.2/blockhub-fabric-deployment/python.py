from fabric.api import *



class python:
    def __init__(self, version):
        self.version = version

    def install(self):
       if self.version == 3.6:
           run('sudo add-apt-repository ppa:deadsnakes/ppa')
           run('sudo apt-get update')
           run('sudo apt-get install python3.6')
