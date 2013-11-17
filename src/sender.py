import argparse, socket, sys
import time

def main():
    args = parse_args()
    rcvrs = len(args.ips)
    
    PORT = 8000
    print args.ips
    st = time.time()
    sckts = []
    
    for i in range(len(args.ips)):
        sckts.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        sckts[-1].connect((args.ips[i], PORT))
    
    with open('../data/%s/storage/%d/%s/chunk%i.csv' %
              (args.ds, args.cs, args.ns, 0)) as f:
        lines = f.readlines()

    start = 0
    done = False
    length = len(lines)

    while not done:
        for i in range(len(args.ips)):
            end = start + args.cs
            if args.debug:
                print '%d\t%d' % (start, end)
                sys.stdout.flush()
            if end >= length:
                end = length
                done = True
            sckts[(i+args.id)%len(args.ips)].sendall(''.join(lines[start:end]))
            if done: break
            start = end

    [ s.close() for s in sckts ]

    print time.time() - st
    sys.stdout.flush()
    # return None

def parse_args():
    parser = argparse.ArgumentParser("Node which will send data.")
    parser.add_argument('--id',
                        action='store',
                        help='ID of this sender')
    parser.add_argument('--cs',
                        action='store',
                        help='Chunk size used for something...',
                        default=500)
    parser.add_argument('--ns',
                        action='store',
                        help='# of senders to be used. Must be >=1.',
                        default=1)
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
    args.ns = int(args.ns)

    args.ips = [ i.strip(',][ ') for i in args.ips ]

    if args.debug:
        print 'id: %d cs: %d rc: %s' % (args.id, args.cs, args.ips)
        sys.stdout.flush()

    return args


if __name__ == '__main__':
    main()
