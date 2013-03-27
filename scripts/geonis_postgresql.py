'''
Postgresql db interface for pasta2geonis workflow

Created on Mar 12, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import psycopg2
import datetime, time
from contextlib import contextmanager
from geonis_pyconfig import dsnfile
from logging import WARN

# some statements now obsolete
##def getPackageInsert():
##    """Returns (statement, valueObject) where valueObject is dict with column names and defaults. Fill in values
##       and execute statement. """
##    stmt = """INSERT INTO workflow.package (packageid, scope, identifier, revision, downloaded)
##     VALUES(%(packageid)s, %(scope)s, %(identifier)s, %(revision)s, %(downloaded)s);"""
##    obj = {'packageid':'','scope':'','identifier':0,'revision':0,'downloaded':datetime.datetime.now()}
##    return (stmt,obj)

##def updateSpatialType(packageId, sType):
##    if sType == "spatialRaster":
##        stmt = "UPDATE workflow.package set israster = TRUE where packageid = %s;"
##    elif sType == "spatialVector":
##        stmt = "UPDATE workflow.package set isvector = TRUE where packageid = %s;"
##    else:
##        return
##    with cursorContext() as cur:
##        cur.execute(stmt, (packageId,))

def getEntityInsert():
    """Returns (statement, valueObject) where valueObject is dict with column names and defaults. Fill in values
       and execute statement. """
    stmt = """INSERT INTO workflow.entity (packageid, entityname, israster, isvector, entitydescription, status)
     VALUES(%(packageid)s, %(entityname)s, %(israster)s, %(isvector)s, %(entitydescription)s, %(status)s);"""
    obj = {'packageid':'', 'entityname':'', 'israster':False, 'isvector':False, 'entitydescription':'', 'status':''}
    return (stmt,obj)

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
        conn = None
        with open(dsnfile) as dsnf:
            dsnStr = dsnf.readline()
        conn = psycopg2.connect(dsn = dsnStr)
        if not conn or conn.closed:
            if conn:
                del conn
            attempt = 1
            while attempt < 5 and (not conn or conn.closed):
                if conn:
                    del conn
                print "attempt:", attempt
                time.sleep(0.5)
                attempt += 1
                conn = psycopg2.connect(dsn = dsnStr)
        if not conn or conn.closed:
            raise Exception("DB connection failed after %d attemps." % (attempt,))
        cur = conn.cursor()
        #enter WITH block with value of cur
        yield cur
    except psycopg2.Warning as warn:
        if conn:
            conn.close()
            del conn
        if logger:
            logger.logMessage(WARN, warn.message)
        else:
            print warn.message
    except (psycopg2.Error, Exception) as err:
        #exiting WITH block with errors
        if conn:
            conn.rollback()
            conn.close()
            del conn
        if logger:
            logger.logMessage(WARN, err.message)
        else:
            print err.message
        raise
    else:
        #exiting WITH block with no errors
        conn.commit()
        del cur
        conn.close()
        del conn



def main():
    pkid = 'knb-lter-rmb.1.2'
    with cursorContext() as cur1:
        stmt = "delete from workflow.entity where packageid = %s;"
        cur1.execute(stmt,(pkid,))
    with cursorContext() as cur2:
        stmt = "delete from workflow.package where packageid = %s;"
        cur2.execute(stmt,(pkid,))

    s,vals = getPackageInsert()
    vals["packageid"] = pkid
    parts = pkid.split('.')
    vals["scope"] = parts[0][9:]
    vals["identifier"] = parts[1]
    vals["revision"] = parts[2]

    with cursorContext() as cur3:
        #print cur1.mogrify(s,vals)
        cur3.execute(s,vals)

    s2, vals2 = getEntityInsert()
    vals2["packageid"] = pkid
    vals2["entityname"] = "e-name"
    vals2["entitydescription"] = "e-desc"

    with cursorContext() as cur5:
        print cur5.mogrify(s2, vals2)
        cur5.execute(s2, vals2)

    updateSpatialType(pkid,'spatialVector')

    with cursorContext() as cur4:
        stmt = "select * from workflow.package left outer join workflow.entity on (workflow.package.packageid = workflow.entity.packageid);"
        cur4.execute(stmt)
        rows = cur4.fetchall()
        for r in rows:
            print str(r)


if __name__ == '__main__':
    #main()
    pass
