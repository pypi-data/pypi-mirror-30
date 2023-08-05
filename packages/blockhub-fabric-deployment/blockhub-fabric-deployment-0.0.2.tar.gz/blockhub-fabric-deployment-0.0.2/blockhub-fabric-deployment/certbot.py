from fabric.api import *
from fabric.contrib.files import append


class certbot:

    @staticmethod
    def install():
        run('sudo apt-get update')
        run('sudo apt-get install software-properties-common')
        run('sudo add-apt-repository ppa:certbot/certbot')
        run('sudo apt-get update')
        run('sudo apt-get install python-certbot-nginx')
        run('sudo certbot --nginx')

    @staticmethod
    def add_cron(user=None):
        """
        Add this to automatically renew certs
        """
        run('sudo crontab -l > /tmp/crondump'.format(user if user else '$USER'))
        append('/tmp/crondump', text='0 4 * * * /usr/bin/certbot renew --quiet', use_sudo=True)
        run('crontab /tmp/crondump')
