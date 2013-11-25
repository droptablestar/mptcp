from mininet.topo import Topo

class nSwitch(Topo):
    def __init__(self, n=1, s=1, r=1, **opts):
        Topo.__init__(self, **opts)
        self.senders = s
        self.receivers = r
        switches = []
        senders = []
        receivers = []
        # create switches
        for i in range(n):
            switches.append(self.addSwitch('s%s' % (i+1)))

        # create senders
        for h in range(s):
            senders.append(self.addHost('h%s' % (h+1)))

        # create receivers
        for h in range(r):
            receivers.append(self.addHost('h%s' % (h+s+1)))

        # connect all senders / receivers to all switches
        for i in range (n):
            for h in range(s):
                self.addLink(senders[h], switches[i])
            for h in range(r):
                self.addLink(receivers[h], switches[i])
                
                

class Test(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        self.addSwitch('4_1_1')

        self.addHost('0_0_2')
        self.addHost('1_0_3')

        self.addLink('0_0_2','4_1_1')
        self.addLink('1_0_3','4_1_1')
