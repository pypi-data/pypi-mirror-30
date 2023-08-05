# vim: set ts=4 sts=4 sw=4 et fileencoding=utf-8:
#
# database related functions for ardj.
#
# ardj is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# ardj is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
ARDJ, an artificial DJ.

This module contains the database related code.
"""

import os

from ardj import config


def transaction(f):
    """The @transaction decorator."""
    def wrapper(*args, **kwargs):
        db = connect()
        db.begin()
        try:
            res = f(*args, **kwargs)
            db.commit()
            return res
        except:
            db.rollback()
            raise
    return wrapper


def connect():
    """Returns the active database instance."""
    db_type = config.get("database", "sqlite")
    if db_type == "sqlite":
        from ardj import database_sqlite
        return database_sqlite.connect()
    elif db_type == "mysql":
        from ardj import database_mysql
        return database_mysql.connect()
    else:
        raise RuntimeError("database type not set")


def cmd_console(*args):
    """Open database console (sqlite3)"""
    from ardj.util import run_replace

    print connect()
    command = connect().console_command()
    run_replace(command)


@transaction
def cmd_init():
    """
    Initialize the database

    Initializes the configured database by executing a set of preconfigured SQL
    instructions.  This is non-destructive.  You should run this after you
    empty the database.
    """

    db = connect()
    db.update_schema()


def cmd_export(arg=None, *args):
    if arg == "help":
        print "Dumps all tables to CSV files: tracks.csv, labels.csv etc."
        exit(1)

    elif arg is not None:
        print "This command takes no argument."
        exit(1)

    import csv
    from ardj.util import utf

    db = connect()

    tables = ["tracks", "labels", "queue", "playlists", "urgent_playlists", "karma", "votes", "playlog", "tasks"]
    for table in tables:
        fn = "%s.csv" % table

        with open(fn, "wb") as f:
            writer = csv.writer(f)
            for row in db.dump_table(table):
                writer.writerow(map(utf, row))

        print "Wrote %s" % fn


def cmd_import(*args):
    if not args:
        print "Please specify CSV files to import."
        exit(1)

    elif args[0] == "help":
        print "Imports data from specified files to database tables."
        print "Table contents is deleted beforehand."
        exit(1)

    import csv
    db = connect()

    fail = False
    for fn in args:
        if not fn.endswith(".csv"):
            print "Argument %s skipped: file name must end with .csv" % fn
            fail = True
            continue

        if not os.path.exists(fn):
            print "File %s not found." % fn
            fail = True
            continue

        try:
            with open(fn, "rb") as f:
                reader = csv.reader(f)

                table_name = os.path.basename(fn)[:-4]
                db.load_table(table_name, reader)

                print "Loaded file %s to table %s" % (fn, table_name)
        except Exception, e:
            print "Error loading %s: %s" % (fn, e)
            fail = True

    if fail:
        print "There were errors."
        exit(1)


@transaction
def cmd_purge():
    """Delete stale data"""
    db = connect()
    db.vacuum()
