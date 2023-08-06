# Cuckoo

## Installation

```bash
$ pip install cuckoo-db
```

## Usage
```bash
# Create a new empty migration
$ cuckoo new helloworld
Migration [./migrations/1523455521_helloworld.py] created successfully!

# Apply all migrations
$ cuckoo migrate up
Migrating [up].
Processing migration [1523455521_helloworld].
Migration complete.

# Remove all migrations
$ cuckoo migrate down
Migrating [down]
Processing migration [1523455521_helloworld].
Migration complete.
```