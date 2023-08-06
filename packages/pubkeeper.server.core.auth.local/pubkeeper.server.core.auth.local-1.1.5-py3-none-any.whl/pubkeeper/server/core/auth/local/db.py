from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from uuid import uuid4
from argparse import Namespace
from hashlib import sha256
import os

from .models import User, Token, Right


class Database(object):
    def __init__(self, database_uri, settings=None):
        self._settings = settings
        try:
            self._engine = create_engine(database_uri)
            self._db = self._engine.connect()
        except OperationalError:
            engine = create_engine(
                database_uri[:database_uri.rfind('/')] + "/postgres",
                isolation_level="AUTOCOMMIT"
            )
            conn = engine.connect()
            conn.execute('create database pk_{}'.format(
                database_uri[database_uri.rfind('/') + 1:]))
            conn.close()
            self._engine = create_engine(database_uri)
            self._db = self._engine.connect()

        self._session_maker = sessionmaker(bind=self._engine)
        self.session = self._session_maker()

        self.init_database(database_uri)

        has_root = \
            self.session.query(User).filter_by(username='root').first()
        if not has_root:
            self.seed_database()

    def init_database(self, database_uri):
        file_directory = os.path.dirname(os.path.realpath(__file__))
        alembic_directory = os.path.join(file_directory, 'alembic')
        ini_path = os.path.join(file_directory, 'alembic.ini')

        # create Alembic config and feed it with paths
        config = Config(ini_path)
        config.set_main_option('script_location', alembic_directory)
        config.cmd_opts = Namespace()

        # If it is required to pass -x parameters to alembic
        x_arg = 'database_uri={}'.format(database_uri)
        if not hasattr(config.cmd_opts, 'x'):
            if x_arg is not None:
                setattr(config.cmd_opts, 'x', [])
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                setattr(config.cmd_opts, 'x', None)

        revision = 'head'
        sql = False
        tag = None
        command.upgrade(config, revision, sql=sql, tag=tag)

    def seed_database(self):
        initial_password = self._settings.get(
            'initial_password', fallback='root')
        initial_token = self._settings.get(
            'initial_token', fallback=sha256(uuid4().bytes).hexdigest())

        user = User(username='root',
                    password=sha256(initial_password.encode()).hexdigest())

        token = Token(token=initial_token,
                      description='Default All Access Token')
        right = Right(token=initial_token, topic='**',
                      read=True, write=True)
        token.rights = [right]

        self.session.add_all([user, token])
        self.session.commit()
