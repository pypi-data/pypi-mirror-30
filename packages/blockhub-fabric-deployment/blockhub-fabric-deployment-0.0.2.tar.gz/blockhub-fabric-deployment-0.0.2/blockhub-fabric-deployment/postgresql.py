from fabric.api import *


class postgresql:
    @staticmethod
    def install(self):
        run('sudo apt-get -y install postgresql postgresql-contrib')

    @staticmethod
    def create_user(username):
        run('sudu -H -u postgres createuser{}'.format(username))

    @staticmethod
    def create_db(db, owner='postgres'):
        run('sudo -H -u postgres createdb {db} --owner {owner}'.format(db=db, owner=owner))

    @staticmethod
    def set_password(user, password, encrypted=True):
        if encrypted:
            run('''sudo -H -u postgres psql -c "ALTER USER {user} WITH ENCRYPTED PASSWORD '{pw}'"'''.format(
                user=user,
                pw=password
            ))
        else:
            run('''sudo -H -u postgres psql -c "ALTER USER {user} WITH PASSWORD '{pw}'"'''.format(
                user=user,
                pw=password
            ))