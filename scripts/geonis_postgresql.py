'''
Postgresql db interface for pasta2geonis workflow

Created on Mar 12, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: Ron Beloin & Jack Peterson
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import psycopg2
import datetime, time
from contextlib import contextmanager
from geonis_pyconfig import dsnfile
from logging import WARN
import pdb

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
    """
    Returns (statement, valueObject) where valueObject is dict 
    with column names and defaults. Fill in values and execute 
    statement.
    """
    sql = (
        "INSERT INTO entity "
        "(packageid, entityname, israster, isvector, entitydescription, status) "
        "VALUES "
        "(%(packageid)s, %(entityname)s, %(israster)s, %(isvector)s, "
        "%(entitydescription)s, %(status)s)"
    )
    parameters = {
        'packageid': '',
        'entityname': '',
        'israster': False,
        'isvector': False,
        'entitydescription': '',
        'status': '',
    }
    return (sql, parameters)

@contextmanager
def cursorContext(logger=None, connect=None):
    """ Provides a wrapper to a generator function that yields a db cursor
        ready to execute a statement. Handles connection, commit, rollback,
        error trapping, and closing connection. Will propagate exceptions.
    Usage:
        with cursorContext() as cur:
            cur.execute(...)
    """
    try:
        conn = None
        if connect is None:
            with open(dsnfile) as dsnf:
                dsnStr = dsnf.readline()
        else:
            with open(connect) as dsnf:
                dsnStr = dsnf.readline()
        conn = psycopg2.connect(dsn=dsnStr)
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
                conn = psycopg2.connect(dsn=dsnStr)
        if not conn or conn.closed:
            raise Exception("DB connection failed after %d attempts." % (attempt,))
        cur = conn.cursor()
        #enter WITH block with value of cur
        yield cur
    except psycopg2.Warning as warn:
        #pdb.set_trace()
        if conn:
            conn.close()
            del conn
        if logger:
            logger.logMessage(WARN, warn.message)
        else:
            print warn.message
    except (psycopg2.Error, Exception) as err:
        #pdb.set_trace()
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

def getConfigValue(name):
    retval = ''
    with cursorContext() as cur:
        cur.execute("SELECT strvalue FROM wfconfig WHERE name = %s", (name,))
        rslt = cur.fetchone()
        if rslt:
            retval = rslt[0]
            del rslt
    return retval

##def main():
##    pkid = 'knb-lter-rmb.1.2'
##    with cursorContext() as cur1:
##        stmt = "delete from workflow.entity where packageid = %s;"
##        cur1.execute(stmt,(pkid,))
##    with cursorContext() as cur2:
##        stmt = "delete from workflow.package where packageid = %s;"
##        cur2.execute(stmt,(pkid,))
##
##    s,vals = getPackageInsert()
##    vals["packageid"] = pkid
##    parts = pkid.split('.')
##    vals["scope"] = parts[0][9:]
##    vals["identifier"] = parts[1]
##    vals["revision"] = parts[2]
##
##    with cursorContext() as cur3:
##        #print cur1.mogrify(s,vals)
##        cur3.execute(s,vals)
##
##    s2, vals2 = getEntityInsert()
##    vals2["packageid"] = pkid
##    vals2["entityname"] = "e-name"
##    vals2["entitydescription"] = "e-desc"
##
##    with cursorContext() as cur5:
##        print cur5.mogrify(s2, vals2)
##        cur5.execute(s2, vals2)
##
##    updateSpatialType(pkid,'spatialVector')
##
##    with cursorContext() as cur4:
##        stmt = "select * from workflow.package left outer join workflow.entity on (workflow.package.packageid = workflow.entity.packageid);"
##        cur4.execute(stmt)
##        rows = cur4.fetchall()
##        for r in rows:
##            print str(r)

def main():
    print getConfigValue("dnsfile")
##    limits = [[u'and', u'1, 2, 3'], [u'rmb', u'20 - 25'], [u'xyz', u'200 '], [u'emp', u'#']]
##    valsArr = []
##    for item in limits:
##        scope = str(item[0]).strip()
##        idlist = []
##        #print scope
##        ids = str(item[1]).strip()
##        if ',' in ids:
##            for idnum in ids.split(','):
##                idlist.append(idnum.strip())
##        elif '-' in ids:
##            rng = ids.split('-')
##            low = int(rng[0].strip())
##            hi = int(rng[1].strip()) + 1
##            for i in range(low,hi):
##                idlist.append(str(i))
##        elif '#' in ids or ids == '':
##            idlist.append('*')
##        else:
##            idlist.append(ids)
##        for idn in idlist:
##            valsArr.append({'inc':'%s.%s' % (scope,idn)})
##    valsTuple = tuple(valsArr)
##    print valsTuple
##    with cursorContext() as cur:
##        stmt = "insert into limit_identifier values(%(inc)s);"
##        cur.executemany(stmt, valsTuple)




if __name__ == '__main__':
    #main()
    pass

