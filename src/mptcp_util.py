#!/usr/bin/python
"""
This util file defines some helper functions for MPTCP
It is adapted from the Mininet MPTCP test file (mininet-tests/mptcp/mptcp_2hNs.py)
"""

import sys
from subprocess import Popen, PIPE
from time import sleep
import termcolor as T
import argparse
from mininet.log import lg

def sysctl_set(key, value):
    """Issue systcl for given param to given value and check for error."""
    p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE,
              stderr=PIPE)
    p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE,
              stderr=PIPE)
    # Output should be empty; otherwise, we have an issue.  
    stdout, stderr = p.communicate()
    stdout_expected = "%s = %s\n" % (key, value)
    if stdout != stdout_expected:
        raise Exception("Popen returned unexpected stdout: %s != %s" %
                        (stdout, stdout_expected))
    if stderr:
        raise Exception("Popen returned unexpected stderr: %s" % stderr)


def set_enabled(enabled):
    """Enable MPTCP if true, disable if false"""
    e = 1 if enabled else 0
    lg.info("setting MPTCP enabled to %s\n" % e)
    sysctl_set('net.mptcp.mptcp_enabled', e)


def set_ndiffports(ports):
    """Set ndiffports, the number of subflows to instantiate"""
    lg.info("setting MPTCP ndiffports to %s\n" % ports)
    sysctl_set("net.mptcp.mptcp_ndiffports", ports)


def debug(onoff):
    onoff = 1 if onoff else 0
    lg.info("setting MPTCP debug to %s\n" % onoff)
    p = Popen("sysctl -w net.mptcp.mptcp_debug=%s" % onoff, shell=True, stdout=PIPE,
              stderr=PIPE)
        # Output should be empty; otherwise, we have an issue.  
    stdout, stderr = p.communicate()
    stdout_expected = "net.mptcp.mptcp_debug = %s\n" % onoff
    if stdout != stdout_expected:
        raise Exception("Popen returned unexpected stdout: %s != %s" %
                        (stdout, stdout_expected))
    if stderr:
        raise Exception("Popen returned unexpected stderr: %s" % stderr)

''' 
Disables MPTCP and resets the number of ports to 1
'''
def reset():
    set_enabled(False)
    debug(False)
    set_ndiffports(1)

def enable_mptcp(mptcp_subflows):
    if mptcp_subflows > 1:
        debug(True)
        set_enabled(True)
        set_ndiffports(mptcp_subflows)
    else:
        reset()

def progress(t):
    while t > 0:
        print T.colored('  %3d seconds left  \r' % (t), 'cyan'),
        t -= 1
        sys.stdout.flush()
        sleep(1)
    print '\r\n'
