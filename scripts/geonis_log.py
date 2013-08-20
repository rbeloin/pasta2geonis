'''
Created on Jan 21, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import os, sys, datetime, traceback, logging
from functools import wraps
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from arcpy import ExecuteError as gpError, GetMessages as gpMessages
from geonis_pyconfig import defaultLoggingLevel
from geonis_postgresql import cursorContext
import psycopg2
import pdb
from pprint import pprint

class EvtLog(object):
    """
    Logger acts as singleton; call getLogger
    with optional name and path to get a logger that can be used for logging.
    """
    singleinstance = None
    def __init__(self, name, fileorpath, showMessages):
        self.evtLogger = logging.getLogger(name)
        self.showMsgs = showMessages
        if fileorpath:
            if not os.path.isfile(fileorpath):
                logfile = os.path.join(fileorpath, "geonis_wf.log")
            else:
                logfile = fileorpath
            fileHandler = logging.FileHandler(logfile)
            #for files, we format with timestamp
            fileHandler.setFormatter(
                logging.Formatter(
                    fmt="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%m/%d/%Y %I:%M:%S %p"
                )
            )
            self.evtLogger.addHandler(fileHandler)
        else:
            self.evtLogger.addHandler(logging.StreamHandler())
        self.evtLogger.setLevel(defaultLoggingLevel)


    @staticmethod
    def getLogger(name = "geonisWF", fileorpath = None, showMessages = False):
        if not EvtLog.singleinstance:
            EvtLog.singleinstance = EvtLog(name, fileorpath, showMessages)
            if fileorpath:
                EvtLog.singleinstance.logMessage(
                    logging.WARN,
                    str(datetime.datetime.now()) + " ***** Log started  with path = " +
                        fileorpath + " and verbose = " + str(showMessages) + " ****"
                )
        return EvtLog.singleinstance

    def logMessage(self, level, msg):
        """ Log to log file, and if showMsgs has been set in init log to arcpy also. If no log
            file has been given, log to std_err """
        try:
            assert self.evtLogger
            self.evtLogger.log(level, msg)
            # if running not optimized, log everthing, changing level as needed
            if __debug__ and not self.evtLogger.isEnabledFor(level):
                self.evtLogger.log(self.evtLogger.getEffectiveLevel(), "<debug mode>" + msg)
            if not self.evtLogger or self.showMsgs:
                if self.showMsgs and (level == logging.INFO or level == logging.DEBUG):
                    arcAddMsg(msg)
                elif level == logging.WARN or level == logging.WARNING:
                    arcAddWarn(msg)
                elif level == logging.ERROR or level == logging.CRITICAL:
                    arcAddErr(msg)
        except Exception as ex:
            print "Exception in logMessage"
            raise ex


def errHandledWorkflowTask(taskName=""):
    """This is a decorator for task methods of tools. It wraps the task function
       in a try block, makes log entries, and will raise Exception if any exceptions are
       raised in the task function. The taskName parameter will show up in log entries.
       This decorator only works for methods of an object, and will look for self.logger
       variable for logging. It logs as warnings because logging an ERROR will call arcpy.AddError,
       which in turn will terminate the program. Usually we just want to terminate processing this
       data set. """
    def decorate(taskFunc):
        @wraps(taskFunc)
        def errHandlingWrapper(*args, **kwargs):
            try:
                if args[0] is None or args[0].logger is None:
                    raise Exception("errHandleWorkflowTask did not find logger instance.")
                logger = args[0].logger
                logger.logMessage(logging.INFO, taskName + ":")
                if 'packageId' in kwargs.keys():
                    if 'entityName' in kwargs.keys():
                        updateReports(
                            taskFunc.__name__,
                            taskName,
                            kwargs['packageId'],
                            entity=kwargs['entityName'],
                            logger=logger
                        )
                    else:
                        updateReports(
                            taskFunc.__name__,
                            taskName,
                            kwargs['packageId'],
                            logger=logger
                        )
                return taskFunc(*args, **kwargs)
            except gpError:
                logger.logMessage(logging.WARN, gpMessages(2))
                raise Exception(gpMessages())
            except Exception as e:
                logger.logMessage(logging.WARN, "error type: " + str(type(e)))
                logger.logMessage(logging.WARN, e.message)
                taskReport = taskName + " terminated: " + e.message
                if 'packageId' in kwargs.keys():
                    if 'entityName' in kwargs.keys():
                        updateReports(
                            taskFunc.__name__,
                            taskName,
                            kwargs['packageId'],
                            entity=kwargs['entityName'],
                            report=taskReport,
                            status='error',
                            logger=logger
                        )
                    else:
                        updateReports(
                            taskFunc.__name__,
                            taskName,
                            kwargs['packageId'],
                            report=taskReport,
                            status='error',
                            logger=logger
                        )
                raise Exception(taskReport)
        return errHandlingWrapper
    return decorate


# Add entry to packagereport/entityreport tables
def updateReports(taskName, taskDesc, pkgId, entity=None, report=None, status='ok', logger=None):

    # Add entries to the report and taskreport tables
    with cursorContext(logger) as cur:

        # If we didn't receive an value for the entity parameter, then this is a
        # package-level report
        if entity is None:
            if logger:
                logger.logMessage(
                    logging.DEBUG,
                    "%s: editing package report for %s" % (taskName, pkgId)
                )

            # If an entry already exists in the report table for thie packageId,
            # then all we need to do is update the taskreport table
            sql = (
                "SELECT reportid FROM report WHERE packageid = %(packageid)s "
                "AND entityname IS NULL"
            )
            parameters = {'packageid': pkgId}
            cur.execute(sql, parameters)
            if cur.rowcount:
                reportId = cur.fetchone()[0]

                # If this reportId/taskName combination already exists in
                # taskreport, then update the row; otherwise, insert a new row.
                sql = (
                    "SELECT COUNT(*) FROM taskreport WHERE "
                    "reportid = %s AND taskname = %s"
                )
                cur.execute(sql, (reportId, taskName))
                if cur.fetchone()[0] > 0:
                    sql = (
                        "UPDATE taskreport SET taskname = %(taskname)s, description = "
                        "%(description)s, report = %(report)s, status = %(status)s "
                        "WHERE reportid = %(reportid)s"
                    )
                else:
                    sql = (
                        "INSERT INTO taskreport "
                        "(reportid, taskname, description, report, status) VALUES "
                        "(%(reportid)s, %(taskname)s, %(description)s, "
                        "%(report)s, %(status)s)"
                    )
            
            # If this is a package we haven't seen before, then we need to create
            # new rows in both the report and taskreport tables
            else:
                # Insert a new row into the report table
                sql = (
                    "INSERT INTO report (packageid) VALUES "
                    "(%(packageid)s) RETURNING reportid"
                )
                cur.execute(sql, parameters)
                reportId = cur.fetchone()[0]

                # Insert a new row into the taskreport table
                sql = (
                    "INSERT INTO taskreport "
                    "(reportid, taskname, description, report, status) VALUES "
                    "(%(reportid)s, %(taskname)s, %(description)s, %(report)s, %(status)s)"
                )

        # Otherwise, we need to add a report on a specific entity
        else:
            if logger:
                logger.logMessage(
                    logging.DEBUG,
                    "%s: editing entity report for %s (%s)" % (taskName, pkgId, entity)
                )

            # If an entry already exists in the report table (for this packageId and
            # entityName combination), then all we need to do is update the taskreport
            # table
            sql = (
                "SELECT reportid FROM report WHERE packageid = %(packageid)s "
                "AND entityname = %(entityname)s"
            )
            parameters = {'packageid': pkgId, 'entityname': entity}
            cur.execute(sql, parameters)
            if cur.rowcount:
                reportId = cur.fetchone()[0]

                # If this reportId/taskName combination already exists in
                # taskreport, then update the row; otherwise, insert a new row.
                sql = (
                    "SELECT COUNT(*) FROM taskreport WHERE "
                    "reportid = %s AND taskname = %s"
                )
                cur.execute(sql, (reportId, taskName))
                if cur.fetchone()[0] > 0:
                    sql = (
                        "UPDATE taskreport SET taskname = %(taskname)s, description = "
                        "%(description)s, report = %(report)s, status = %(status)s "
                        "WHERE reportid = %(reportid)s"
                    )
                else:
                    sql = (
                        "INSERT INTO taskreport "
                        "(reportid, taskname, description, report, status) VALUES "
                        "(%(reportid)s, %(taskname)s, %(description)s, "
                        "%(report)s, %(status)s)"
                    )

            # If this is an entity we haven't seen before, then we need to get the
            # entityId from the entity table and use it to create a new row in the
            # report and taskreport tables
            else:

                # Get the entityId from the entity table
                pdb.set_trace()
                sql = (
                    "SELECT id FROM entity WHERE packageid = %(packageid)s "
                    "AND entityname = %(entityname)s"
                )
                cur.execute(sql, parameters)
                parameters['entityid'] = cur.fetchone()[0]

                # Insert a new row into the report table
                sql = (
                    "INSERT INTO report (packageid, entityid, entityname) VALUES "
                    "(%(packageid)s, %(entityid)s, %(entityname)s) RETURNING reportid"
                )
                cur.execute(sql, parameters)
                reportId = cur.fetchone()[0]

                # Insert a new row into the taskreport table
                sql = (
                    "INSERT INTO taskreport "
                    "(reportid, taskname, description, report, status) VALUES "
                    "(%(reportid)s, %(taskname)s, %(description)s, %(report)s, %(status)s)"
                )

        # Finally, execute the insert or update query
        parameters = {
            'reportid': reportId,
            'taskname': taskName,
            'description': taskDesc,
            'report': report,
            'status': True if status == 'ok' else False,
        }
        cur.execute(sql, parameters)
