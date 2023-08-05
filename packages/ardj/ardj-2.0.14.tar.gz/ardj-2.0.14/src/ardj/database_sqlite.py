# encoding=utf-8

import time

from sqlite3 import dbapi2 as sqlite
from sqlite3 import OperationalError

from ardj import get_data_path, config
from ardj.database import transaction
from ardj.log import *


class SQLiteDatabase(object):
    conn = None

    def __init__(self):
        filename = config.get_path("sqlite_database", "~/.ardj/database.sqlite")
        if not filename:
            raise RuntimeError("sqlite_database config value not set")

        self.filename = filename
        self.db = sqlite.connect(self.filename, check_same_thread=False)

        self.db.create_collation("utf8_unicode_ci", self.sqlite_ucmp)
        self.db.create_function("ULIKE", 2, self.sqlite_ulike)

    def sqlite_ucmp(self, a, b):
        return cmp(lower(a), lower(b))

    def sqlite_ulike(self, a, b):
        if a is None or b is None:
            return None
        if ardj.util.lower(b) in ardj.util.lower(a):
            return 1
        return 0

    @classmethod
    def connect(cls):
        if cls.conn is None:
            cls.conn = cls()
        return cls.conn

    def begin(self):
        self.execute("BEGIN")

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def execute(self, query, params=None):
        last_e = None

        for attempt in range(5):
            try:
                cur = self.db.cursor()
                cur.execute(query, params or [])
                if query.startswith("INSERT"):
                    return cur.lastrowid
                else:
                    return cur.rowcount
            except Exception, e:
                last_e = e
                if "database is locked" in str(e):
                    log_warning("Database locked, will retry in 5 seconds: {}", query)
                    time.sleep(5)
                else:
                    raise

        raise e

    def fetch(self, query, params=None):
        cur = self.db.cursor()
        cur.execute(query, params or [])

        while True:
            row = cur.fetchone()
            if row is None:
                break
            yield row

        cur.close()

    def fetch_dict(self, query, params=None):
        cur = self.db.cursor()
        cur.execute(query, params or [])

        fields = [f[0] for f in cur.description]

        while True:
            row = cur.fetchone()
            if row is None:
                break

            yield dict(zip(fields, row))

        cur.close()

    def console_command(self):
        return ["sqlite3", "-header", self.filename]

    def update_schema(self):
        script = get_data_path("sqlite_init.sql")
        with open(script, "rb") as f:
            for line in f.readlines():
                if line.startswith("--"):
                    continue

                elif not line.strip():
                    continue

                try:
                    self.execute(line)
                except:
                    print "Init statement failed: %s" % line
                    raise

    def dump_table(self, table_name):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM `%s`" % table_name)

        fields = [f[0] for f in cur.description]
        yield fields

        while True:
            row = cur.fetchone()
            if row is None:
                break

            yield row

        cur.close()

    @transaction
    def load_table(self, table_name, rows):
        cur = self.db.cursor()
        cur.execute("DELETE FROM `%s`" % table_name)

        query = None
        for row in rows:
            if query is None:
                fields = ", ".join(["`%s`" % f for f in row])
                marks = ", ".join(["?"] * len(row))
                query = "INSERT INTO `%s` (%s) VALUES (%s)" % (table_name, fields, marks)

            else:
                cur.execute(query, row)

    def vacuum(self):
        """
        Removes stale data.

        Stale data in queue items, labels and votes linked to tracks that no
        longer exist.  In addition to deleting such links, this function also
        analyzed all tables (to optimize indexes) and vacuums the database.
        """
        old_size = os.stat(self.filename).st_size
        for table in ('playlists', 'tracks', 'queue', 'urgent_playlists', 'labels', 'karma'):
            self.execute('ANALYZE ' + table)
        self.execute('VACUUM')
        log_info('{} bytes saved after database purge.', os.stat(self.filename).st_size - old_size)


def connect():
    return SQLiteDatabase.connect()
