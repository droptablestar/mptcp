import Partitioner,sys

def main():
    if len(sys.argv) < 2:
        print 'Usage: python createPartitions data_name num_partitions [chunk_size]'
        exit()
    dname = sys.argv[1]
    if len(sys.argv) > 3: cSize = int(sys.argv[3])
    else: cSize = 0

    fname='../data/%s/train.csv' % dname

    createPartitions(dname, nChunks = int(sys.argv[2]), chunkSize = cSize)

def createPartitions(dname, nChunks, chunkSize):
    print 'Creating %d chunks chunk size: %d for set: %s' % \
        (nChunks,chunkSize,dname)
    partitioner = Partitioner.Partitioner(dname, nChunks,
                                          chunkSize = chunkSize)
    partitioner.partition()


if __name__ == '__main__':
    main()
