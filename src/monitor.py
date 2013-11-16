from select import poll, POLLIN
from subprocess import Popen, PIPE
import time

def monitorFiles( outfiles, seconds, timeout ):
    "Monitor set of files and return [(host, line)...]"
    devnull = open( '/dev/null', 'w' )
    tails, fdToFile, fdToHost = {}, {}, {}
    for h, outfile in outfiles.iteritems():
        tail = Popen( [ 'tail', '-f', outfile ],
                      stdout=PIPE, stderr=devnull )
        fd = tail.stdout.fileno()
        tails[ h ] = tail
        fdToFile[ fd ] = tail.stdout
        fdToHost[ fd ] = h
        # Prepare to poll output files
        readable = poll()
        for t in tails.values():
            readable.register( t.stdout.fileno(), POLLIN )
        # Run until a set number of seconds have elapsed
        endTime = time.time() + seconds
        while time.time() < endTime:
            fdlist = readable.poll(timeout)
            if fdlist:
                for fd, _flags in fdlist:
                    f = fdToFile[ fd ]
                    host = fdToHost[ fd ]
                    # Wait for a line of output
                    line = f.readline().strip()
                    yield host, line
            else:
                # If we timed out, return nothing
                yield None, ''
        for t in tails.values():
            t.terminate()
        devnull.close()  # Not really necessary
