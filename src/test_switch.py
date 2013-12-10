#!/usr/bin/python
import os, socket, thread, time, argparse, sys
from subprocess import Popen, PIPE
from monitor import monitorFiles
from dctopo import TwoHostNInterfaceTopo
import termcolor as T

from mininet.log import lg
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch as Switch
from mininet.util import custom
from mptcp_util import reset, progress, set_enabled, set_ndiffports

def main(args):
    topo = TwoHostNInterfaceTopo(n=args.n)
    link = custom(TCLink, bw=args.bw)
    net = Mininet(topo=topo, switch=Switch, link=link)
    set_enabled(args.mptcp)
    set_ndiffports(args.ndiffports)
    net.start()
    
    h1 = net.getNodeByName('h1')
    h2 = net.getNodeByName('h2')
    for j in range(args.n):
        h1.cmdPrint('ifconfig h1-eth%i 10.0.%i.1 netmask 255.255.255.0' %
                      (j, j))
        h2.cmdPrint('ifconfig h2-eth%i 10.0.%i.2 netmask 255.255.255.0' %
                      (j, j))

        if args.mptcp:
            dev = 'h1-eth%i' % (j)
            h1.cmdPrint('ip rule add from 10.0.%i.1 table %i' % (j, j+1))
            h1.cmdPrint('ip route add 10.0.%i.0/24 dev %s scope link table %i' \
                              % (j, dev, j+1))
            h1.cmdPrint('ip route add default via 10.0.%i.1 dev %s table %s'\
                              % (j, dev, j+1))

    if args.debug:
        outfiles = {h: '/tmp/%s.out' % h.name for h in net.hosts}
        errfiles = {h: '/tmp/%s.out' % h.name for h in net.hosts}
        [ h.cmd('echo >',outfiles[h]) for h in net.hosts ]
        [ h.cmd('echo >',errfiles[h]) for h in net.hosts ]
        
    if args.debug:
        h2.sendCmd('python receiver.py --id %d --nr %d --ns %d --ds %s --debug'
                   %(0, 1, 1, args.ds),
                   '>', outfiles[h2],
                   '2>', errfiles[h2])
    else:
        h2.sendCmd('python receiver.py --id %d --nr %d --ns %d --ds %s'
                                 %(0, 1, 1, args.ds))
            
    ips = [ h2.IP() ]
    
    time.sleep(1)
    if args.debug:
        h1.sendCmd('python sender.py --id %d --ns %d --ips %s --ds %s --debug'\
                       % (0, 1, ips, args.ds),
                   '>', outfiles[h1],
                   '2>', errfiles[h1])
    else:
        h1.sendCmd('python sender.py --id %d --cs %d --ns %d --ips %s --ds %s'\
                       % (0, 500, 1, ips, args.ds))
            
    tts = {}
    ttr = {}
    p = Popen(['./timer.py'])
    tts[h1] = h1.waitOutput()
    ttr[h2] = h2.waitOutput()

    p.kill()
    print tts.values()
    print ttr.values()
    write_results(tts, ttr, args)
    net.stop()
    reset()
                
def parse_args():
    parser = argparse.ArgumentParser(description="2-host n-switch test")
    parser.add_argument('--bw',
                        action="store",
                        help="Bandwidth of links",
                        default=10)
    parser.add_argument('-n',
                        action="store",
                        help="Number of switches.  Must be >= 1",
                        default=2)
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

def write_results(tts, ttr, args):
    if not os.path.exists('../results/sw%s' %
                          (args.n)):
        os.makedirs('../results/sw%s' % (args.n))

    if args.mptcp:
        f = open('../results/sw%s/bw%s_nf%s_mptcp.csv' %
                 (args.n,args.bw,args.ndiffports), 'a')
    else:
        f = open('../results/sw%s/bw%s_nf%s.csv' %
                 (args.n,args.bw,args.ndiffports), 'a')
    f.write('%s,%s\n' %
            (','.join(map(lambda x: x.strip('\n'), tts.values())),
             ','.join(map(lambda x: x.strip('\n'), ttr.values()))))

    f.close()

if __name__ == '__main__':
    try:
        # lg.setLogLevel('info')
        args = parse_args()
        main(args)
    except:
        import traceback
        traceback.print_exc(file=sys.stdout)
        reset()
        os.system("mn -c; killall controller")
