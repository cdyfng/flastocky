#!/usr/bin/env python
# name IsOpen.py
import os, subprocess
import socket
import psutil
import logging
logging.basicConfig(level=logging.DEBUG,\
    format='%(asctime)s|%(filename)s|%(funcName)s|line:%(lineno)d|%(levelname)s|%(message)s',
    datefmt='%Y-%m-%d %X',
    filename=os.path.dirname(os.path.abspath(__file__)) +'/checkService.log'
    )

def IsOpen(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port)))
        s.shutdown(2)
        print '%d is open' % port
        return True
    except:
        print '%d is down' % port
        return False

def runPyService(pyname):
    INTERPRETER = "/usr/bin/python"
    if not os.path.exists(INTERPRETER):
        print "Cannot find INTERPRETER at path \"%s\"." % INTERPRETER
    processor = pyname

    pargs = [INTERPRETER, processor]
    pargs.extend(["--input=inputMd5s"])
    subprocess.Popen(pargs)


def isRunning(cmd):
    pids = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        if cmd in str(p.cmdline()):
            logging.info('%s :%s' %(cmd,p.status()))
            mem_percent = p.memory_percent()
            if mem_percent > 25.0:
                p.kill()
                logging.info('percent :%f' % mem_percent)
                return False
            return pid
    return False


def checkService(arg2):
    #logging.info('CS in %s', str(arg2))
    if isRunning(arg2) == False:
        logging.info('not running')
        INTERPRETER = "/usr/bin/python"
        if not os.path.exists(INTERPRETER):
            print "Cannot find INTERPRETER at path \"%s\"." % INTERPRETER
            logging.info('no interppeter')
        processor = os.path.dirname(os.path.abspath(__file__)) \
            + '/manage.py'
        pargs = [INTERPRETER, processor, arg2]
        subprocess.Popen(pargs)
        logging.info('%s', str(pargs))


if __name__ == '__main__':
    #if IsOpen('127.0.0.1',8000) != True:
    #    runPyService(\
    #    os.path.dirname(os.path.abspath(__file__)) + '/yourpyfile.py')
    #logging.info('start check')
    checkService('crawler')
    checkService('notify')




