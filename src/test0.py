#!/usr/bin/python
import os, socket, thread, time, argparse, sys
from subprocess import Popen, PIPE
from monitor import monitorFiles
from topo import nSwitch
import termcolor as T

from mininet.log import lg
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch as Switch
from mininet.util import custom

def test0(args):
    topo = nSwitch(n=args.n, s=args.s, r=args.r)
    link = custom(TCLink, bw=args.bw)
    net = Mininet(topo=topo, switch=Switch, link=link)
    setup(args)
    net.start()

    print net.pingAll()
    senders = net.hosts[:topo.senders]
    receivers = net.hosts[topo.senders:]
    mkdirs(args)

    for i in range(1,len(senders)+1):
        host = net.getNodeByName('h%i' % i)
        for j in range(args.n):
            host.cmdPrint('ifconfig h%i-eth%i 10.0.%i.%i netmask 255.255.255.0' %
                                (i, j, j, i))
            if args.mptcp:
                dev = 'h%i-eth%i' % (i, j)
                host.cmdPrint('ip rule add from 10.0.%i.%i table %i' % (j, i, j+1))
                host.cmdPrint('ip route add 10.0.%i.0/24 dev %s scope link table %i' % (j, dev, j+1))
                host.cmdPrint('ip route add default via 10.0.%i.1 dev %s table %s' % (j, dev, j+1))

    for i in range(len(senders)+1,len(senders)+len(receivers)+1):
        host = net.getNodeByName('h%i' % i)
        for j in range(args.n):
            host.cmdPrint('ifconfig h%i-eth%i 10.0.%i.%i netmask 255.255.255.0' %
                                (i, j, j, i))
        
    if args.debug:
        outfiles = {h: '/tmp/%s.out' % h.name for h in net.hosts}
        errfiles = {h: '/tmp/%s.out' % h.name for h in net.hosts}
        [ h.cmd('echo >',outfiles[h]) for h in net.hosts ]
        [ h.cmd('echo >',errfiles[h]) for h in net.hosts ]
        
    for r in range(len(receivers)):
        if args.debug:
            receivers[r].sendCmd('python receiver.py --id %d --nr %d --ns %d --ds %s --debug'
                                 %(r, len(receivers), len(senders), args.ds),
                                 '>', outfiles[receivers[r]],
                                 '2>', errfiles[receivers[r]])
        else:
            receivers[r].sendCmd('python receiver.py --id %d --nr %d --ns %d --ds %s'
                                 %(r, len(receivers), len(senders), args.ds))

    ips = [ r.IP() for r in receivers ]

    time.sleep(1)
    for s in range(len(senders)):
        if args.debug:
            senders[s].sendCmd('python sender.py --id %d --ns %d --ips %s --ds %s --debug' %
                               (s, len(senders), ips, args.ds),
                               '>', outfiles[senders[s]],
                               '2>', errfiles[senders[s]])
        else:
            senders[s].sendCmd('python sender.py --id %d --cs %d --ns %d --ips %s --ds %s' %
                               (s, len(senders), ips, args.ds))

    # if args.debug:
    #     for h, line in monitorFiles(outfiles, 50, timeout=500):
    #         if h:
    #             print('%s: %s' % (h.name, line))
            
    tts = {}
    ttr = {}
    for s in senders:
        tts[s] = s.waitOutput()
    for r in receivers:
        ttr[r] = r.waitOutput()

    print tts
    print ttr
    print 'here'
    net.stop()

def progress(t):
    while t > 0:
        print T.colored('  %3d seconds left  \r' % (t), 'cyan'),
        t -= 1
        sys.stdout.flush()
        time.sleep(1)
    print '\r\n'

def mkdirs(args):
    try:
        os.makedirs('../data/%s/received/%d/%d' %
                    (args.ds, args.cs, args.r))
    except Exception, e:
        # print 'fail',e
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="2-host n-switch test")
    parser.add_argument('--bw',
                        action="store",
                        help="Bandwidth of links",
                        default=10)
    parser.add_argument('-n',
                        action="store",
                        help="Number of switches.  Must be >= 1",
                        default=1)
    parser.add_argument('-s',
                        action="store",
                        help="Number of senders.  Must be >= 1",
                        default=1)
    parser.add_argument('-r',
                        action="store",
                        help="Number of receivers.  Must be >= 1",
                        default=1)
    parser.add_argument('--mptcp',
                        action="store_true",
                        help="Enable MPTCP (net.mptcp.mptcp_enabled)",
                        default=False)
    parser.add_argument('--ndiffports',
                        action="store",
                        help="Set # subflows (net.mptcp.mptcp_ndiffports)",
                        default=1)
    parser.add_argument('--ds',
                        action="store",
                        help="Dataset to use.",
                        default='covtype')
    parser.add_argument('--cs',
                        action="store",
                        help="Size of chunks to be used for...something.",
                        default=500)
    parser.add_argument('--debug',
                        action="store_true",
                        help="Turn on debugging",
                        default=False)

    args = parser.parse_args()
    args.n = int(args.n)
    args.s = int(args.s)
    args.r = int(args.r)
    return args

def set_mptcp_enabled(enabled):
    """Enable MPTCP if true, disable if false"""
    e = 1 if enabled else 0
    lg.info("setting MPTCP enabled to %s\n" % e)
    sysctl_set('net.mptcp.mptcp_enabled', e)

def set_mptcp_ndiffports(ports):
    """Set ndiffports, the number of subflows to instantiate"""
    lg.info("setting MPTCP ndiffports to %s\n" % ports)
    sysctl_set("net.mptcp.mptcp_ndiffports", ports)

def sysctl_set(key, value):
    """Issue systcl for given param to given value and check for error."""
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

def setup(args):
    set_mptcp_enabled(args.mptcp)
    set_mptcp_ndiffports(args.ndiffports)

def end(args):
    set_mptcp_enabled(False)
    set_mptcp_ndiffports(1)

if __name__ == '__main__':
    lg.setLogLevel('info')
    args = parse_args()
    test0(args)
    end(args)
