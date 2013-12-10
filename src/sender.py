"""This script emulates a node which sends data to a number of receivers. Each
sender will open a unique copy of the data and send it divided evenly amongst
all the receivers (passed in as an array of IPs to send to).
"""
import argparse, socket, sys, time

from subprocess import call

def main():
    args = parse_args()
    rcvrs = len(args.ips)

    PORT = 8000
    st = time.time()
    sckts = []

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

    for i in range(len(args.ips)):
        sckts.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        sckts[-1].connect((args.ips[i], PORT))
    
    with open('../data/%s/train%i.csv' % (args.ds, args.id)) as f:
        lines = f.readlines()

    start = 0
    done = False
    length = len(lines)

    while not done:
        for i in range(len(args.ips)):
            end = start + args.cs
            if end >= length:
                end = length
                done = True
            if args.debug:
                print '%d sending %d-%d to %d' % \
                    (args.id,start,end,(i+args.id)%len(args.ips))
                sys.stdout.flush()

            sckts[(i+args.id)%len(args.ips)].sendall(''.join(lines[start:end]))

            if done: break
            start = end

    map(lambda s: s.close(), sckts)

    print time.time() - st

def parse_args():
    parser = argparse.ArgumentParser("Node which will send data.")
    parser.add_argument('--id',
                        action='store',
                        help='ID of this sender')
    parser.add_argument('--cs',
                        action='store',
                        help='Chunk size used for something...',
                        default=500)
    parser.add_argument('--ds',
                        action='store',
                        help='Dataset to use for distribution.',
                        default='covtype')
    parser.add_argument('--ips',
                        nargs='*',
                        help='List of ip addresses of receivers.')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Turns on debugging mode.',
                        default=False)

    args = parser.parse_args()
    args.id = int(args.id)
    args.cs = int(args.cs)
    args.ips = [ i.strip(',][ ') for i in args.ips ]

    if args.debug:
        print 'id: %d cs: %d rc: %s' % (args.id, args.cs, args.ips)
        sys.stdout.flush()

    return args


if __name__ == '__main__':
    main()
