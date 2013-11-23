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
        self.addSwitch('a1')
        self.addSwitch('a2')

        self.addSwitch('e1')
        self.addSwitch('e2')

        self.addHost('h1')
        self.addHost('h2')
        self.addHost('h3')
        self.addHost('h4')

        self.addLink('e1','h1')
        self.addLink('e1','h2')
        self.addLink('e1','a1')
        self.addLink('e1','a2')

        self.addLink('e2','h3')
        self.addLink('e2','h4')
        self.addLink('e2','a1')
        self.addLink('e2','a2')


