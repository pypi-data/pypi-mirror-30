from cuckoo.cuckoo import Migrator
from cuckoo.db import Database
from cuckoo.migration import MIGRATION_TEMPLATE, Migration

import fire
import os
import time


DEFAULT_MIGRATION_PATH = "./migrations"
DEFAULT_DB_CONFIG = "config.json"


class Runner(object):

    @staticmethod
    def migrate(direction, migration_path=DEFAULT_MIGRATION_PATH, config=DEFAULT_DB_CONFIG):
        db = Database.get_instance(config)
        Migration._meta.database = db
        migrator = Migrator(db, migration_path)
        migrator.run(direction)

    @staticmethod
    def new(name, migration_path=DEFAULT_MIGRATION_PATH):
        timestamp = int(time.time())
        filename = os.path.join(migration_path, str(timestamp) + '_' + str(name) + '.py')

        with open(filename, 'a') as outfile:
            outfile.write(MIGRATION_TEMPLATE)
        
        print(f'Migration [{filename}] created successfully!')


def main():
    fire.Fire(Runner)

if __name__ == '__main__':
    main()