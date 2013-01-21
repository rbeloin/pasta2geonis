'''
Created on Jan 21, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import os
import logging
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn

defaultLoggingLevel = logging.INFO

class EvtLog(object):
    """
    Logger acts as singleton; call getLogger
    with optional name and path to get a logger that can be used for logging.
    """
    singleinstance = None
    def __init__(self, name, fileorpath):
        self.evtLogger = logging.getLogger(name)
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
        self.evtLogger.info("*************** Logging started ***************")


    @staticmethod
    def getLogger( name = "geonisWF", fileorpath = None):
        if not EvtLog.singleinstance:
            EvtLog.singleinstance = EvtLog(name, fileorpath)
        return EvtLog.singleinstance

    def logMessage(self, level, verbose, msg):
        """ Log to log file, and if verbose log to arcpy also. If no log
            file has been given, log to std_err """
        try:
            assert self.evtLogger
            self.evtLogger.log(level, msg)
            # if running not optimized, log everthing, changing level as needed
            if __debug__ and not self.evtLogger.isEnabledFor(level):
                self.evtLogger.log(self.evtLogger.getEffectiveLevel(), "<debug mode>" + msg)
            if not self.evtLogger or verbose:
                if verbose and (level == logging.INFO or level == logging.DEBUG):
                    arcAddMsg(msg)
                elif level == logging.WARN or level == logging.WARNING:
                    arcAddWarn(msg)
                elif level == logging.ERROR or level == logging.CRITICAL:
                    arcAddErr(msg)
        except Exception as ex:
            print "Exception in logMessage"
            raise ex






