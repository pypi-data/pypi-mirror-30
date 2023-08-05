# encoding=utf-8

import datetime
import threading

import MySQLdb
import MySQLdb.constants.FIELD_TYPE as ftype
import MySQLdb.constants.CLIENT as client_constants

from ardj import get_data_path, config
from ardj.log import log_debug


def _unicode(v):
    if isinstance(v, str):
        return v.decode("utf-8")
    return unicode(v)


def _date_decode(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError, e:
        return None


CONVERTERS = {
    ftype.DECIMAL: float,
    ftype.NEWDECIMAL: float,
    ftype.DOUBLE: float,
    ftype.FLOAT: float,
    ftype.INT24: int,
    ftype.LONG: int,
    ftype.LONGLONG: int,
    ftype.SHORT: int,
    ftype.TINY: int,
    ftype.BIT: int,

    ftype.CHAR: _unicode,
    ftype.STRING: _unicode,
    ftype.VARCHAR: _unicode,
    ftype.VAR_STRING: _unicode,
    ftype.BLOB: str,
    ftype.MEDIUM_BLOB: str,

    ftype.DATE: _date_decode,
    ftype.DATETIME: lambda v: datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S"),
}


class MySQLDatabase(object):
    def __init__(self):
        self.user = config.get("mysql_login")
        self.passwd = config.get("mysql_password")
        self.base = config.get("mysql_database")
        self.debug = config.get("mysql_debug") == "yes"

        self.conn = MySQLdb.connect(
            user=self.user,
            passwd=self.passwd,
            db=self.base,
            conv=CONVERTERS,
            client_flag=client_constants.FOUND_ROWS,
            autocommit=False)

        self.conn.set_character_set("utf8")

        cur = self.conn.cursor()
        cur.execute("SET NAMES utf8")
        cur.close()

    @classmethod
    def tls(cls):
        key = "mysql_connections"

        t = threading.currentThread()
        if not hasattr(t, key):
            setattr(t, key, {})
        return getattr(t, key)

    @classmethod
    def connect(cls):
        """
        Returns an open connection.
        Connection pool is maintained in the TLS.
        """
        key = "mysql_conn"

        t = threading.currentThread()
        if not hasattr(t, key):
            setattr(t, key, cls())
        return getattr(t, key)

    def begin(self):
        self.conn.begin()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def execute(self, query, params=None):
        cur = self.conn.cursor()
        res = cur.execute(self.format_query(query, params))
        if query.startswith("INSERT"):
            return cur.lastrowid
        else:
            return cur.rowcount

    def fetch(self, query, params=None):
        cur = self.conn.cursor()
        cur.execute(self.format_query(query, params))

        while True:
            row = cur.fetchone()
            if row is None:
                break
            yield map(self.deutf, row)

        cur.close()

    def fetch_dict(self, query, params=None):
        cur = self.conn.cursor()
        cur.execute(self.format_query(query, params))

        fields = [x[0] for x in cur.description]

        while True:
            row = cur.fetchone()
            if row is None:
                break
            yield dict(zip(fields, map(self.deutf, row)))

        cur.close()

    def console_command(self):
        return ["mysql", "-u" + self.user, "-p" + self.passwd, self.base]

    def update_schema(self):
        script = get_data_path("mysql_init.sql")
        with open(script, "rb") as f:
            for line in f:
                query = line.strip()
                if not query:
                    continue
                if query.startswith("--"):
                    continue

                try:
                    print query
                    self.execute(query)
                except Exception, e:
                    if "Duplicate key name" in str(e):
                        pass
                    else:
                        raise

    def load_table(self, table_name, rows):
        self.begin()

        def cell(value):
            if value == "None":
                return None
            if isinstance(value, unicode):
                return value.encode("utf-8")
            return value


        try:
            query = None
            header = None

            self.execute("DELETE FROM `%s`" % table_name)

            for row in rows:
                if query is None:
                    header = row
                    fields = ", ".join(["`%s`" % f for f in row])
                    marks = ", ".join(["?"] * len(row))
                    query = "INSERT INTO `%s` (%s) VALUES (%s)" % (table_name, fields, marks)

                else:
                    try:
                        self.execute(query, map(cell, row))
                    except Exception, e:
                        print "Bad row for %s: %s" % (table_name, row)
                        raise

            self.commit()

        except Exception, e:
            self.rollback()
            raise

    def vacuum(self):
        pass

    def format_query(self, query, args=None):
        if not args:
            if self.debug:
                log_debug("SQL: {}", query)
            return query

        parts = query.split("?")
        if len(parts) != len(args) + 1:
            raise RuntimeError("wrong argument count")

        for idx, part in enumerate(parts[:-1]):
            arg = args[idx]
            if arg is None:
                arg = "NULL"
            elif isinstance(arg, (int, float)):
                arg = str(arg)
            elif isinstance(arg, unicode):
                arg = self.conn.escape_string(arg.encode("utf-8"))
                arg = "'%s'" % arg
            else:
                arg = self.conn.escape_string(arg)
                arg = "'%s'" % arg

            parts[idx] += arg

        query = "".join(parts)

        if self.debug:
            log_debug("SQL: {}", query)
        return query

    def deutf(self, value):
        if isinstance(value, str):
            return value.decode("utf-8")
        return value


def connect():
    return MySQLDatabase.connect()
