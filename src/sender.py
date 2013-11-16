import argparse, socket
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', action='store')
    parser.add_argument('--cs', action='store')
    parser.add_argument('--rc', nargs='*')

    args = parser.parse_args()
    args.id = int(args.id)
    args.cs = int(args.cs)

    # print 'id: %d cs: %d' % (args.id, args.cs)
    args.rc = [ i.strip(',][ ') for i in args.rc ]
    # print 'rc:',args.rc
    rcvrs = len(args.rc)
    
    HOST = str(args.rc[0])
    PORT = 8000

    st = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    with open('../data/covtype/storage/%d/%s/chunk%s.csv' %
              (args.cs, rcvrs, args.id)) as f:
        lines = f.readlines()

    start = 0 if args.id==0 else 1
    done = False
    length = len(lines)
    while not done:
        end = start + args.cs
        if end >= length:
            end = length
            done = True
        s.sendall(''.join(lines[start:end]))
        start = end
    s.close()

    print time.time() - st
    return None

if __name__ == '__main__':
    main()
