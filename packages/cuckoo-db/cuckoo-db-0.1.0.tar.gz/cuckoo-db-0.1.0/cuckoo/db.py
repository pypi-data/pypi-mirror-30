from peewee import Expression, OP
from playhouse.postgres_ext import PostgresqlExtDatabase

import json
import os


OP.update(DISTANCE_BETWEEN='distance_between')


def distance_between(lhs, rhs):
    return Expression(lhs, OP.DISTANCE_BETWEEN, rhs)


class Database(object):
    __DB__ = None

    @staticmethod
    def _register_ops():
        PostgresqlExtDatabase.register_ops({
            OP.DISTANCE_BETWEEN: '<->'
        })
    
    @classmethod
    def get_instance(cls, cfg_path):
        if Database.__DB__ is None:
            Database.set_db(cfg_path)
        
        return Database.__DB__
        
    @classmethod
    def set_db(cls, cfg_path):
        # Must register operators before DB is instantiated
        # See : https://github.com/coleifer/peewee/issues/599
        cls._register_ops()

        with open(cfg_path, 'r') as infile:
            config = json.load(infile)

        Database.__DB__ = PostgresqlExtDatabase(
            database=config['db_name'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            register_hstore=False
        )