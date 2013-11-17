##############################################################################
# Author: Josh Reese                                                         #
# Purdue Univerity Fall 2013                                                 #
# As part of a project to investigate the impact of data distribution in a   #
# distributed random forest algorithm.                                       #
##############################################################################
##############################################################################
# This class will take a dataset, read it from disk and create chunks of     #
# data which can be partitioned in various ways.                             #
# Current partitioning schemes: round robin, random shuffle.                 #
##############################################################################

import random,os

class Partitioner:
    # parameters:
    # dname: the name of the data set
    # numChunks: the number of chunk files to produce
    # ptype: the type of partitioning to use
    def __init__(self, dname, numChunks=2, chunkSize=0):
        self.dname = dname
        self.numChunks = int(numChunks);
        self.chunkSize = int(chunkSize)

    # this is the main method, call this to create the partitions
    def partition(self):
        self.__part()
        
    # this is a standard partitioning scheme. chunk the data into partitions as
    # evenly distributed as possible. round robin style.
    def part(self):
        # list of file descriptors. one for each chunk
        self.__makedirs()
        fds = [ open('../data/%s/storage/%d/%d/chunk%d.csv' %
                     (self.dname,self.chunkSize,self.numChunks,i),'w')
                for i in xrange(self.numChunks) ]

        with open('../data/%s/train.csv' % self.dname,'r') as f:
            lines = f.readlines()
        lines = map(lambda x: x.strip(' \n'), lines)

        header = lines.pop(0)
        for x in fds: x.write('%s\n' % header)

        length = len(lines)
        if self.chunkSize == 0:
            self.chunkSize = length / self.numChunks

        linenum=0
        while linenum < length:
            for i in range(self.numChunks):
                count = 0
                while count < self.chunkSize and linenum < length:
                    fds[i].write('%s\n' % lines[linenum])
                    count += 1
                    linenum += 1
        [ x.close for x in fds ]

    def mkdirs(self):
        try:
            os.makedirs('../data/%s/storage/%d/%d' %
                        (self.dname,self.chunkSize,self.numChunks))
        except:
            # print 'fail'
            pass
        
    __makedirs = mkdirs
    __part = part
