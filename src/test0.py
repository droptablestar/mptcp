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
    topo = nSwitch(n=args.n)
    link = custom(TCLink, bw=args.bw)
    net = Mininet(topo=topo, switch=Switch, link=link)
    setup(args)
    net.start()

    senders = net.hosts[:topo.senders]
    receivers = net.hosts[topo.senders:]
    mkdirs(500, len(receivers))

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
        
    # h1 = net.getNodeByName('h1')
    # h2 = net.getNodeByName('h2')
    # h2.sendCmd('iperf -s -i 1')
    # print h1.cmdPrint('ping -c 1 %s' % h2.IP())
    # h1.sendCmd('iperf -c %s -t 2 -i 1' % h2.IP())
    # progress(3)
    # h1_out = h1.waitOutput()
    # lg.info('sender:\n%s\n' % h1_out)
    # time.sleep(0.1)
    # h2_out = h2.read(10000)
    # lg.info('receiver:\n%s\n' % h2_out)
    # net.stop()
    # end(args)
    # exit(0)
    if args.debug:
        routfiles = {h: '/tmp/r%s.out' % h.name for h in receivers}
        rerrfiles = {h: '/tmp/r%s.out' % h.name for h in receivers}
        [ h.cmd('echo >',routfiles[h]) for h in receivers ]
        [ h.cmd('echo >',rerrfiles[h]) for h in receivers ]

    for r in range(0,len(receivers)):
        if args.debug:
            receivers[r].sendCmd('python receiver.py --id %d --cs %d --nr %d --ns %d --debug'
                                 %(r, 500, len(receivers), len(senders)),
                                 '>', routfiles[receivers[r]],
                                 '2>', rerrfiles[receivers[r]],
                                 '&')
        else:
            receivers[r].sendCmd('python receiver.py --id %d --cs %d --nr %d --ns %d'
                                 %(r, 500, len(receivers), len(senders)))

    ips = [ r.IP() for r in receivers ]

    time.sleep(1)
    for s in range(len(senders)):
        senders[s].sendCmd('python sender.py --id %d --cs %d --rc %s' %
                            (s, 500, ips))


    if args.debug:
        for h, line in monitorFiles(routfiles, 50, timeout=500):
            if h:
                print('%s: %s' % (h.name, line))
            
    tts = {}
    for s,r in zip(senders,receivers):
        print r.waitOutput()
        tts[s] = float(s.waitOutput().strip('\n'))
    print tts
    print 'here'
    net.stop()

def progress(t):
    while t > 0:
        print T.colored('  %3d seconds left  \r' % (t), 'cyan'),
        t -= 1
        sys.stdout.flush()
        time.sleep(1)
    print '\r\n'

def mkdirs(chunkSize, numChunks):
    try:
        os.makedirs('../data/covtype/received/%d/%d' %
                    (chunkSize, numChunks))
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
    parser.add_argument('--mptcp',
                        action="store_true",
                        help="Enable MPTCP (net.mptcp.mptcp_enabled)",
                        default=False)
    parser.add_argument('--ndiffports',
                        action="store",
                        help="Set # subflows (net.mptcp.mptcp_ndiffports)",
                        default=1)
    parser.add_argument('--debug',
                        action="store_true",
                        help="Turn on debugging",
                        default=False)

    args = parser.parse_args()
    args.n = int(args.n)
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
