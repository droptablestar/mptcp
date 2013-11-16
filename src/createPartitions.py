import Partitioner,sys

def main():
    if len(sys.argv) < 2:
        print 'Usage: python createPartitions data_name [chunk_size]'
        exit()
    dname = sys.argv[1]
    if len(sys.argv) > 2: cSize = int(sys.argv[2])
    else: cSize = 0

    fname='../data/%s/train.csv' % dname

    for i in [1]:
        createPartitions(dname, nChunks = i, chunkSize = cSize)

def createPartitions(dname, nChunks, chunkSize):
    print 'Creating %d chunks chunk size: %d for set: %s' % \
        (nChunks,chunkSize,dname)
    partitioner = Partitioner.Partitioner(dname, nChunks,
                                          chunkSize = chunkSize)
    partitioner.partition()


if __name__ == '__main__':
    main()
