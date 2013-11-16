import argparse, socket, threading, sys

bufs = []

def receiver():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', action='store')
    parser.add_argument('--cs', action='store')
    parser.add_argument('--nr', action='store')
    parser.add_argument('--ns', action='store')
    parser.add_argument('--debug', action='store_true', default=False)

    args = parser.parse_args()
    print 'id: %s cs: %s nr: %s ns: %s' % (args.id, args.cs, args.nr, args.ns)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    HOST = ''
    PORT = 8000
    s.bind((HOST, PORT))

    s.listen(1)
    conn, addr = s.accept()
    print 'connection: ', addr
    t = threading.Thread(target=rcv_data, args=(conn, 0, args.debug))
    t.start()
    t.join()
    conn.close()

    writer(args)
    
def rcv_data(conn, tid, debug):
    global bufs
    bufs.append('')

    rcvd = 0
    while 1:
        data = conn.recv(65536)
        if not data: break
        if debug:
            rcvd+=1
            if rcvd % 5000 == 0:
                print '%i lines received.' % rcvd
                sys.stdout.flush()
        bufs[tid] += data
        
def writer(args):
    fd = open('../data/covtype/received/%s/%s/chunk%s.csv' %
             (args.cs, args.nr, args.id),'w')
    for i in range(len(bufs)):
        fd.write(bufs[i])
        
    fd.close()
        
if __name__ == '__main__':
    receiver()
