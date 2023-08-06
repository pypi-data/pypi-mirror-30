import getpass
from astrosql.config import get_config
from peewee import *


def connect(database=None, user=None, password=None, host=None):
    """Returns an instance of MySQL database (peewee.MySQLDatabase)."""
    config = get_config()
    HOST = config['mysql'].get('host', 'localhost')
    DATABASE = config['mysql'].get('database')
    USER = config['mysql'].get('user')
    PASSWORD = config['mysql'].get('password')

    database = DATABASE if not database else database
    user = USER if not user else user
    password = PASSWORD if not password else password
    host = HOST if not host else host

    assert database, "No database provided in argument or configuration. Please check argument or 'config.yml'"
    assert host, "No host provided in argument or configuration. Please check argument or 'config.yml'"

    if not user or not password:
        user = input('Username: ')
        password = getpass.getpass()

    return MySQLDatabase(database=database, user=user, password=password, host=host)


# def connect(database=None, user=None, password=None, host=None):
#     """Returns connection instance of a MySQL database."""
#     database = DATABASE if not database else database
#     user = USER if not user else user
#     password = PASSWORD if not password else password
#     host = HOST if not host else host
#
#     assert database, "No database provided in argument or configuration. Please check argument or 'config.yml'"
#     assert host, "No host provided in argument or configuration. Please check argument or 'config.yml'"
#
#     if not user or not password:
#         user = input('Username: ')
#         password = getpass.getpass()
#
#     uri = 'mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(user, password, host, database)
#     engine = create_engine(uri)
#     engine.begin()
#     return engine
