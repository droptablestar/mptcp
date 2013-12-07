#!/usr/bin/python

import termcolor as T
import sys, time
t = 1
while True:
    print T.colored('  %3d seconds since start  \r' % (t), 'cyan'),
    t += 1
    sys.stdout.flush()
    time.sleep(1)
print '\r%s\n' % ' '*80
sys.stdout.flush()
