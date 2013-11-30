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
                
                

class DualHomedTop(Topo):
    def __init__(self, k=4):
        Topo.__init__(self)

        self.addSwitch('0_0_1')
        self.addHost('0_0_3')
        self.addLink('0_0_3', '0_0_1', 0, 0)

        self.addSwitch('0_0_2')
        self.addHost('0_0_3')
        self.addLink('0_0_3', '0_0_2', 1, 0)

        self.addSwitch('0_0_2')
        self.addHost('0_0_4')
        self.addLink('0_0_4', '0_0_2', 0, 1)

        # self.addSwitch('e1')
        # self.addHost('h1')
        # self.addLink('h1','e1')
        # self.addHost('h2')
        # self.addLink('h2','e1')

        # self.addSwitch('e2')
        # self.addHost('h1')
        # self.addLink('h1','e2')
        # self.addHost('h2')
        # self.addLink('h2','e2')

        


topos = { 'dht' : (lambda: DualHomedTop()) }
