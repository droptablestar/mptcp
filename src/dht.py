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

        for e in range(1,3):
            self.addSwitch('e%i' % e)

            self.addHost('h%i' % 1)
            self.addHost('h%i' % 2)
            self.addHost('h%i' % 3)
            self.addHost('h%i' % 4)

            self.addLink('h%i' % 1, 'e%i' % e)
            self.addLink('h%i' % 2, 'e%i' % e)
            self.addLink('h%i' % 3, 'e%i' % e)
            self.addLink('h%i' % 4, 'e%i' % e)

        
        self.addSwitch('a%i' % 1)
        self.addLink('e%i' % 1, 'a%i' % 1)
        self.addLink('e%i' % 2, 'a%i' % 1)

        # self.addSwitch('a%i' % 1)
        # self.addSwitch('a%i' % 2)
        # self.addLink('e%i' % 1, 'a%i' % 1)
        # self.addLink('e%i' % 1, 'a%i' % 2)
        # self.addLink('e%i' % 2, 'a%i' % 1)
        # self.addLink('e%i' % 2, 'a%i' % 2)

        # self.addLink('e%i' % 1, 'a%i' % 1)
        # self.addLink('e%i' % 1, 'a%i' % 2)
        # self.addLink('e%i' % 2, 'a%i' % 1)
        # self.addLink('e%i' % 2, 'a%i' % 2)

topos = { 'dht' : (lambda: DualHomedTop()) }
