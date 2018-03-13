#/usr/bin/python
import threading

PRINT_DEBUG = 1
PRINT_INFO = 4
PRINT_WARNING = 6
PRINT_ERROR = 8
PRINT_LEVEL = 4

print_lock = threading.Lock()

def init(level):
    global PRINT_LEVEL
    PRINT_LEVEL = level
    print "prink level is %d " % PRINT_LEVEL

def print_info(level, info):
    if (level >= PRINT_LEVEL):
        print_lock.acquire()
        if level >= PRINT_ERROR:
            print "ERROR:",
        elif level >= PRINT_WARNING:
            print "WARNING:",
        elif level >= PRINT_INFO:
            print "INFO:",
        else:
            print "DEBUG:",
        print "%s" % info
        print_lock.release()

if __name__ == '__main__':
    init(PRINT_DEBUG)
    print_info(PRINT_DEBUG, "level = 1")
