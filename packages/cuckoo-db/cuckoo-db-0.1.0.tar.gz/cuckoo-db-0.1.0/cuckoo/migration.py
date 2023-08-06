from cuckoo.db import Database

from peewee import CharField, Model


MIGRATION_TEMPLATE = """from playhouse.migrate import migrate

def up(db, migrator):
    pass

def down(db, migrator):
    pass
"""


class Migration(Model):
    migration_id = CharField()

    class Meta:
        database = None