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
            fileHandler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"))
            self.evtLogger.addHandler(fileHandler)
        else:
            self.evtLogger.addHandler(logging.StreamHandler())
        self.evtLogger.setLevel(defaultLoggingLevel)


    @staticmethod
    def getLogger( name = "geonisWF", fileorpath = None, showMessages = False):
        if not EvtLog.singleinstance:
            EvtLog.singleinstance = EvtLog(name, fileorpath, showMessages)
            if fileorpath:
                EvtLog.singleinstance.logMessage(logging.WARN,str( datetime.datetime.now()) + " ***** Log started  with path = " + fileorpath + " and verbose = " + str(showMessages) + " ****")
        return EvtLog.singleinstance

    def logMessage(self, level, msg):
        """ Log to log file, and if showMsgs has been set in init log to arcpy also. If no log
            file has been given, log to std_err """
        try:
            assert self.evtLogger
            self.evtLogger.log(level, msg)
            print msg
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


def errHandledWorkflowTask(taskName = ""):
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
                return taskFunc(*args, **kwargs)
            except gpError:
                logger.logMessage(logging.WARN, gpMessages(2))
                raise Exception(gpMessages())
            except Exception as e:
                logger.logMessage(logging.WARN, "error type: " + str(type(e)))
                logger.logMessage(logging.WARN, e.message)
                raise Exception(taskName + " terminated: " + e.message)
        return errHandlingWrapper
    return decorate






