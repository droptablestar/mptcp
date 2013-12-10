import argparse, os
import numpy as np
import matplotlib.pyplot as plt

# parser = argparse.ArgumentParser()
# parser.add_argument('-f', dest="files", nargs='+', required=True)
# parser.add_argument('-o', dest="out", default=None)
# parser.add_argument('-w', dest="workload", default=None)

# args = parser.parse_args()

if not os.path.exists('../plots'):
    os.makedirs('../plots')
    
dirs = filter(lambda x: 'sw' in x, os.listdir('../results'))

flow1T, flow1M = [], []
for d in sorted(dirs):
    # print d
    rtimesT, rtimesM = [], []
    stdT, stdM = [], []
    for f in sorted(os.listdir('../results/%s' % d)):
        print f
        rtmpM, rtmpT, ftmpT, ftmpM = [], [], [], []
        for line in open('../results/%s/%s' % (d,f)).readlines():
            serv,recv = line.strip('\n').split(',')
            if 'mptcp' in f:
                rtmpM.append(float(recv))
                if 'nf1' in f:
                    ftmpM.append(float(recv))
            else:
                rtmpT.append(float(recv))
                if 'nf1' in f:
                    ftmpT.append(float(recv))
        if 'mptcp' in f:
            rtimesM.append(np.mean(rtmpM))
            stdM.append(np.std(rtmpM))
            if 'nf1' in f:
                flow1M.append(np.mean(ftmpM))
        else:
            rtimesT.append(np.mean(rtmpT))
            stdT.append(np.std(rtmpT))
            if 'nf1' in f:
                flow1T.append(np.mean(ftmpT))

    # print rtimesT
    # print rtimesM
    data = []
    stds = []

    data = rtimesT + rtimesM
    stds = stdT + stdM

    print data
    print stds

    fig = plt.figure()
    ax = plt.gca()
    N = len(data)
    labels = ['TCP'] + range(1,N)
    xaxis = range(N)

    # print('N:%s labels: %s xaxis: %s' % (N, labels, xaxis))
    plt.bar(xaxis, data, 0.5, yerr=stds, color='0.45', ecolor='k')

    plt.title('2 Hosts %s switches N flow(s)' % d[-1])
    plt.xlabel("No. of subflows")
    plt.ylabel("Time (s)")

    xaxis = [ n+0.25 for n in range(N) ]
    ax.set_xticks(xaxis)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max(data) + 5)
    
    plt.savefig('../plots/hist_%s.png' % d)
    # plt.show()

data = []
for t,m in zip(flow1T, flow1M):
    data.append(t)
    data.append(m)

fig = plt.figure()
ax = plt.gca()

N = len(data)
labels = range(2, N / 2 + 2)

colors = ['0.4', '0.1'] * N

xaxis = []
offset = 0
for i in range(N / 2):
    xaxis.append(i+offset)
    xaxis.append(i+offset+0.5)
    offset += 0.5

# print('N:%s labels: %s xaxis: %s' % (N, labels, xaxis))

rects = plt.bar(xaxis, data, 0.5, color=colors, ecolor='k')

plt.title('2 Hosts N switches 1 subflow')
plt.xlabel("No. of switches")
plt.ylabel("Time (s)")

xaxis = xaxis[1::2]
ax.set_xticks(xaxis)
ax.set_xticklabels(labels)
ax.legend(rects, ('TCP', 'MPTCP'))
plt.ylim(0, max(data) + 5)

# plt.show()
plt.savefig('../plots/hist_all.png')
