#!/usr/bin/env python

import os
import sys
import time
import pprint
import signal
import thread
import threading     as mt
import radical.pilot as rp
import radical.utils as ru

import inspect

user   = 'andre-merzky'
passwd = 'z1nfandel'

rp.Session.autopilot(user, passwd)

sys.exit()

print(inspect.getargspec(ru.get_logger))

print ru.__file__
print ru.get_logger
print type(ru.get_logger)
log = ru.get_logger('radical.pilot.test', level='INFO')
log.info('hi logger')

sys.exit()

if not isinstance(mt.current_thread(), mt._MainThread):
    import thread
    thread.interrupt_main()


def test():
    time.sleep(3)
    thread.interrupt_main()

try:
    t = mt.Thread(target=test)
    t.start()
    time.sleep(5)
except KeyboardInterrupt:
    print 'Caught KBI'
except Exception as e:
    print 'caught %s' % e
    raise

# import pycallgraph 
#
# def test():
#     N     = 1000
#     start = time.time()
#     
#     for n in range(N):
#         cud = rp.ComputeUnitDescription()
#         cud.executable = '/bin/sleep'
#         cud.arguments  = ['1s']
#         sys.stdout.write('.')
#         sys.stdout.flush()
#     
#     print
#     
#     stop = time.time()
#     print stop-start
# 
# 
#     
# prof = False
# if prof:
#     from pycallgraph import PyCallGraph
#     from pycallgraph.output import GraphvizOutput
#     
#     with PyCallGraph(output=GraphvizOutput()):
#         test()
# 
# else:
#     test()

