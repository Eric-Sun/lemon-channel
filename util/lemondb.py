#!/usr/bin/env python

import itertools
import logging
import time
import datetime

try:
    import MySQLdb
except:
    pass

try:
    import sqlite3
except:
    pass

def connect(jclassname, **args):
    #sys.path.append(os.getcwd()+'')
    if(jclassname == "mysql"):
        return Mysqldb(**args)
    elif(jclassname == "sqlite"):
        return Sqlitedb(**args)

class LemonDB(object):
    def __init__(self, **kvargs):
        #print 'base class __init__'
        max_idle_time=7*3600
        self.max_idle_time = max_idle_time
        self._db_args = kvargs
        self._last_use_time = time.time()
        self._connect()

    def __del__(self):
        self.close()
        #print 'base class close'

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_conn", None) is not None:
            self._conn.close()
            self._conn = None
        #else:
            #print 'no have _conn attr'

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._connect()
        self._conn.autocommit(True)

    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._excursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(itertools.izip(column_names, row)) for row in cursor]
        finally:
            self.close()

    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        else:
            return rows[0]
        
    def getint(self, query, *parameters):
        """Returns the first row returned for the given query."""
        cursor = self._excursor()
        try:
            self._execute(cursor, query, parameters)
            for row in cursor:
                if row[0]:
                    return int(row[0])
                else:
                    return 0
        finally:
            self.close()
        
    def checkExist(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return False
        else:
            return True
            
    def getone(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        else:
            if len(rows) > 1:
                raise Exception("Multiple rows returned for Database.get() query")
            else:
                return rows[0]

    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._excursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        finally:
            self.close()

    def executemany(self, query, parameters):
        """Executes the given query against all tqueryhe given param sequences.

        We return the lastrowid from the query.
        """
        cursor = self._excursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            self.close()

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self._conn is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _excursor(self):
        self._ensure_connected()
        return self._cursor

    def _execute(self, cursor, query, parameters):
        try:
            return cursor.execute(query, parameters)
        except RuntimeError:
            logging.error("Error connecting to MySQL on %s", self.host)
            self.close()
            raise


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
        
class Sqlitedb(LemonDB):
    def _connect(self):
        self._database = self._db_args["db"]
        sqlite3.register_converter('DATE', self._adapt_converter)
        self._conn = sqlite3.connect(self._database,detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.isolation_level=None
        self._conn.text_factory = str
        #self._conn.row_factory = dict_factory
        self._cursor = self._conn.cursor()
        
    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._connect()

    def _get(self, sql, *args):
        self._cursor.execute(sql)
        return self._cursor.fetchone()
    
    def _execute(self, cursor, query, parameters):
        query = query.replace('%s','?')
        try:
            return cursor.execute(query, parameters)
        except RuntimeError:
            logging.error("Error connecting to SQLITE on %s", self.host)
            self.close()
            raise
    
    def _adapt_converter(self,datestr):
        if datestr:
            now = time.strptime(datestr, "%Y-%m-%d %X")
            return datetime.datetime(*now[:6])
        
        
        
class Mysqldb(LemonDB):
    def _connect(self):
        self._conn = MySQLdb.connect(**self._db_args)
        self._cursor = self._conn.cursor()

if __name__ == '__main__':
    #db = connect("sqlite", db="e:/sqlite/blog.db")
    db = connect("mysql", host="localhost", user="root", passwd="", db="blog")
    
    result = db.getint("select count(*) from typecho_contents")
    print result
    #result = db.execute("insert into entries(id, title) values(%s, %s)", 5, 'test');
    #print result
