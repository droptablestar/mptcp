from mininet.topo import Topo

class nSwitch(Topo):
    def __init__(self, n=1, s=1, r=1, **opts):
        Topo.__init__(self, **opts)
        self.senders = s
        self.receivers = r

        for i in range(1,n+1):
            switch = self.addSwitch('s%i' % i)

            for h in range(s):
                host = self.addHost('h%s' % (h+1))
                self.addLink(host, switch)

            for h in range(s, r+s):
                host = self.addHost('h%s' % (h+1))
                self.addLink(host, switch)
