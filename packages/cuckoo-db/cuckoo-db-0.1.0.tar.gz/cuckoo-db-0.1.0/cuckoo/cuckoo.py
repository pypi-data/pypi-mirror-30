from cuckoo.migration import Migration

from peewee import ProgrammingError
from playhouse.reflection import Introspector
from playhouse.migrate import PostgresqlMigrator

import importlib.util
import os


class Migrator(object):

    def __init__(self, db, path):
        self.db = db
        self._path = path

        self._introspector = Introspector.from_database(self.db)
        self.models = self._introspector.generate_models()
        self.migration_ids = [filename.split('.')[0] for filename in filter(lambda f: f.endswith('.py') and '__init__' not in f, sorted(os.listdir(self._path)))]
    
    def _load_migration(self, m_id):
        module_name = f'{os.path.relpath(self._path).replace("/", ".")}.{m_id}'

        spec = importlib.util.spec_from_file_location(module_name, os.path.join(self._path, f'{m_id}.py'))
        m_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m_mod)

        return m_mod
    
    def _apply_single_migration(self, pg_migrator, direction, migration_id, fn):
        with self.db.atomic():
            try:
                print(f'Processing migration [{migration_id}].')
                fn(self.db, pg_migrator)

                if direction == 'up':
                    Migration(migration_id=migration_id).save()
                elif direction == 'down':
                    Migration.delete().where(Migration.migration_id == migration_id).execute()
            
            except Exception as e:
                print(f'An error occured while processing migration [{migration_id}]: \n\t- {e}')
                raise RuntimeError

    def try_enable_postgis(self):
        try:
            self.db.execute_sql('CREATE EXTENSION postgis;')
            print('Successfully registered postgis.')
        except ProgrammingError:
            self.db.rollback()
    
    def try_prepare_migrations(self):
        self.db.create_tables([Migration], safe=True)
    
    def apply(self, direction):
        applied_migration_ids = set([m.migration_id for m in Migration.select().execute()])
        pg_migrator = PostgresqlMigrator(self.db)

        if direction == 'up':
            ids = filter(lambda m: m not in applied_migration_ids, self.migration_ids)
        elif direction == 'down':
            ids = filter(lambda m: m in applied_migration_ids, self.migration_ids[::-1])
        
        applied_atleast_one = False
        for m_id in ids:
            applied_atleast_one = True
            fn = getattr(self._load_migration(m_id), direction)

            try:
                self._apply_single_migration(pg_migrator, direction, m_id, fn)
            
            except RuntimeError:
                break
        
        if not applied_atleast_one:
            print('Nothing to do.')

    def run(self, direction):
        print(f'Migrating [{direction}].')
        self.try_enable_postgis()
        self.try_prepare_migrations()

        # Apply migrations
        self.apply(direction)
        
        print('Migration complete.')