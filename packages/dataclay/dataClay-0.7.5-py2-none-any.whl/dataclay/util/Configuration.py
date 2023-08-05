'''
Created on Mar 1, 2018

@author: dgasull
'''
from datetime import datetime

'''
Configuration flags. TODO: parse from a file
'''
    
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

""" ===== SESSION CONTROL ==== """
CHECK_SESSION = False
    
""" ===== GARBAGE COLLECTOR ===== """
""" Percentage to start flushing objects """
GC_MEMORY_PRESSURE_PERCENT = 75.0
    
""" Constant. Number of seconds to check if Heap needs to be cleaned. """
GC_CHECK_TIME_INTERVAL = 10.0

""" Global GC collection interval """
NOCHECK_SESSION_EXPIRATION = datetime.strptime('2120-09-10T20:00:04', DATE_FORMAT)
