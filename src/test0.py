#!/usr/bin/python
import os, socket, thread, time, argparse, sys
import termcolor as T

from re import search
from random import choice, shuffle
from subprocess import Popen, PIPE
from monitor import monitorFiles
from topo import nSwitch, Test

from mininet.log import lg
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.util import custom

from mptcp_util import enable_mptcp, reset
from dctopo import FatTreeTopo

def parse_args():
    parser = argparse.ArgumentParser(description="2-host n-switch test")
    parser.add_argument('-bw',
                        action="store",
                        help="Bandwidth of links",
                        default=10)
    parser.add_argument('-sw',
                        action="store",
                        help="Number of switches.  Must be >= 1",
                        default=1)
    parser.add_argument('-ns',
                        action="store",
                        help="Number of senders.  Must be >= 1",
                        default=1)
    parser.add_argument('-nr',
                        action="store",
                        help="Number of receivers.  Must be >= 1",
                        default=1)
    parser.add_argument('-nflows',
                        action="store",
                        help="Set # subflows",
                        default=1)
    parser.add_argument('-ds',
                        action="store",
                        help="Dataset to use.",
                        default='covtype')
    parser.add_argument('-cs',
                        action="store",
                        help="Size of chunks to be used for...something.",
                        default=500)
    parser.add_argument('--mptcp',
                        action="store_true",
                        help="Enable MPTCP (net.mptcp.mptcp_enabled)",
                        default=False)
    parser.add_argument('--debug',
                        action="store_true",
                        help="Turn on debugging",
                        default=False)

    args = parser.parse_args()
    args.bw = int(args.bw)
    args.sw = int(args.sw)
    args.ns = int(args.ns)
    args.nr = int(args.nr)
    args.nflows = int(args.nflows)
    return args

def main():
    K=4
    args = parse_args()
    pox_c = Popen("exec ~/pox/pox.py --no-cli riplpox.riplpox --topo=ft,%s --routing=hashed --mode=reactive 1> /tmp/pox.out 2> /tmp/pox.out" % K, shell=True)
    time.sleep(1) # wait for controller to start

    topo = FatTreeTopo(K)
    # topo = Test()
    link = custom(TCLink, bw=args.bw, max_queue_size=100)
    # net = Mininet(topo=topo, link=link)
    net = Mininet(controller=RemoteController, topo=topo, link=link,
                  switch=OVSKernelSwitch)
    net.start()

    mappings = create_mappings(args, net)
    time.sleep(3)
    
    sndrs = mappings['s']
    rcvrs = mappings['r']

    print 's:',map(lambda x: x.name, mappings['s'])
    print 'r:',map(lambda x: x.name, mappings['r'])

    enable_mptcp(args.nflows)

    for s in sndrs:
        for r in rcvrs:
            s.cmdPrint('ping -c 1 %s' % r.IP())

    # net.pingAll()
    # return

    if args.debug:
        outfiles = {h: '/tmp/%s.out' % h.name for h in net.hosts}
        errfiles = {h: '/tmp/%s.out' % h.name for h in net.hosts}
        [ h.cmd('echo >',outfiles[h]) for h in net.hosts ]
        [ h.cmd('echo >',errfiles[h]) for h in net.hosts ]

    for r in rcvrs:
        if args.debug:
            r.sendCmd('python receiver.py --id %s --nr %d --ns %d --ds %s --debug'
                      % (r.name, args.nr, args.ns, args.ds),
                      '1>', outfiles[r],
                      '2>', errfiles[r])
        else:
            r.sendCmd('python receiver.py --id %s --nr %i --ns %i --ds %s' 
                      % (r, args.nr, args.ns, args.ds))

    time.sleep(1) # let servers start up

    ips = map(lambda x: x.IP(), rcvrs)

    for s,i in zip(sndrs,range(len(sndrs))):
        if args.debug:
            s.sendCmd('python sender.py --id %s --cs %d --ns %d --ips %s --ds %s --debug' 
                      % (i, args.cs, args.ns, ips, args.ds),
                      '1>', outfiles[s],
                      '2>', errfiles[s])
        else:
            s.sendCmd('python sender.py --id %s --cs %d --ns %d --ips %s --ds %s' %
                      (i, args.cs, args.ns, ips, args.ds))

    tts = {}
    ttr = {}
    for s in sndrs:
        tts[s] = s.waitOutput()
    for r in rcvrs:
        ttr[r] = r.waitOutput()

    print tts.values()
    print ttr.values()

    # kill pox controller
    pox_c.kill()
    pox_c.wait()
    
    net.stop()

    write_results(tts, ttr, args)

def write_results(tts, ttr, args):
    if not os.path.exists('../results'):
        os.makedirs('../results')

    if args.mptcp:
        f = open('../results/bw%s_sw%i_ns%i_nr_%i_nf%i_%s_mptcp.csv' %
                 (args.bw,args.sw,args.ns,args.nr,args.nflows,args.ds), 'w')
    else:
        f = open('../results/bw%s_sw%i_ns%i_nr_%i_nf%i_%s.csv' %
                 (args.bw,args.sw,args.ns,args.nr,args.nflows,args.ds), 'w')
    f.write('%s\n%s\n' %
            (','.join(map(lambda x: x.strip('\n'), tts.values())),
             ','.join(map(lambda x: x.strip('\n'), ttr.values()))))

    f.close()
    

def create_mappings(args, net):
    s_hosts = filter(lambda x: search('[02468]_\d_\d',x.name), net.hosts)
    r_hosts = filter(lambda x: search('[13579]_\d_\d',x.name), net.hosts)

    # shuffle(s_hosts)
    # shuffle(r_hosts)
    
    mappings = {'s' : [], 'r' : []}

    for s in range(args.ns):
        mappings['s'].append(s_hosts[s])

    for r in range(args.nr):
        mappings['r'].append(r_hosts[r])

    return mappings
    
if __name__ == '__main__':
    try:
        lg.setLogLevel('info')
        main()
    except:
        import traceback
        reset()
        traceback.print_exc(file=sys.stdout)
        os.system("killall python2.7; mn -c")
