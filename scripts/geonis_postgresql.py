'''
Postgresql db interface for pasta2geonis workflow

Created on Mar 12, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import psycopg2
from contextlib import contextmanager
from geonis_pyconfig import dsnfile
from logging import WARN, ERROR

@contextmanager
def cursorContext(logger = None):
    """ Provides a wrapper to a generator function that yields a db cursor
        ready to execute a statement. Handles connection, commit, rollback,
        error trapping, and closing connection. Will propagate exceptions.
    Usage:
        with cursorContext() as cur:
            cur.execute(...)
    """
    try:
        with open(dsnfile) as dsnf:
            dsnStr = dsnf.readline()
        conn = psycopg2.connect(dsn = dsnStr)
        cur = conn.cursor()
        #enter WITH block with value of cur
        yield cur
    except psycopg2.Warning as warn:
        conn.close()
        del conn
        if logger:
            logger.logMessage(WARN, warn.message)
        else:
            print warn.message
    except psycopg2.Error as err:
        #exiting WITH block with errors
        conn.rollback()
        conn.close()
        del conn
        if logger:
            logger.logMessage(ERROR, err.message)
        else:
            print err.message
        raise
    else:
        #exiting WITH block with no errors
        conn.commit
        del cur
        conn.close()
        del conn



##def main():
##    with cursorContext() as mycur:
##        stmt = "select * from geonis.weather w where w.city = 'salem';"
##        mycur.execute(stmt)
##        rows = mycur.fetchall()
##        for r in rows:
##            print str(r)
##
##
##if __name__ == '__main__':
##    main()
