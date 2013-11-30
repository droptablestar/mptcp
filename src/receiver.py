import argparse, socket, threading, sys, time, os

from subprocess import call

bufs = []

def receiver():
    args = parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    HOST = ''
    PORT = 8000
    s.bind((HOST, PORT))

    s.listen(5)

    connections, tid, st = 0, 0, 0
    thrds = []
    conns = []
    start = time.time()

    # conn, addr = s.accept()
    # print 'accepted'
    # sys.stdout.flush()
    # for i in range(60):
    #     data = conn.recv(65536)
    #     print '%s: %i' % (data, i)
    # print time.time() - start
    # conn.close()

    # return

    while connections < args.ns:
        try:
            conn, addr = s.accept()

            if connections == 0:
                st = time.time()
            
            conns.append(conn)
            connections += 1
            thrds.append(threading.Thread(target=rcv_data, args=(conns[-1],
                                                                 tid,
                                                                 args.debug)))
            tid += 1
            thrds[-1].start()
        except:
            print 'receiver timed out!'
            break

    map(lambda t: t.join(), thrds)
    map(lambda c: c.close(), conns)

    print time.time() - st
    writer(args)
    
def rcv_data(conn, tid, debug):
    global bufs
    bufs.append('')

    rcvd = 0
    while 1:
        data = conn.recv(65536)

        if not data: break
        if debug:
            rcvd += len(data)
            if rcvd >= 100000:
                print '%i bytes received. from: %i' % (len(bufs[tid]), tid)
                sys.stdout.flush()
                rcvd = 0
        bufs[tid] += data

def writer(args):
    path = '../data/%s/received/%i/%i/' % (args.ds, args.cs, args.nr)
        
    if args.debug:
        print map(lambda x: x.count('\n'), bufs)
        sys.stdout.flush()

    if not os.path.exists(path):
        os.makedirs(path)

    fd = open(path+'chunk%s.csv' % args.id, 'w')
    for i in range(len(bufs)):
        fd.write(bufs[i])
        
    fd.close()
    return None

def parse_args():
    parser = argparse.ArgumentParser('Will receive data sent by the sender.')
    parser.add_argument('--id',
                        action='store',
                        help='ID of this node.')
    parser.add_argument('--cs',
                        action='store',
                        help='Chunk size used for...something.',
                        default=500)
    parser.add_argument('--nr',
                        action='store',
                        help='# of receivers to use. Must be >= 1.',
                        default=1)
    parser.add_argument('--ns',
                        action='store',
                        help='# of senders to use. Must be >= 1.',
                        default=1)
    parser.add_argument('--ds',
                        action='store',
                        help='Dataset to be used.',
                        default='covtype')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Turns on debugging mode.',
                        default=False)

    args = parser.parse_args()
    args.cs = int(args.cs)
    args.nr = int(args.nr)
    args.ns = int(args.ns)

    if args.debug:
        print 'id: %s cs: %s nr: %s ns: %s' % (args.id, args.cs, args.nr, args.ns)
        sys.stdout.flush()
    return args

if __name__ == '__main__':
    receiver()
