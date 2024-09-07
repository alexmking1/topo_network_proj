#!/usr/bin/env python

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.node import RemoteController

class AssignmentNetworks(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        
	    # switch performance parameters based on level
        # BANDWIDTH 
        lvl1_bw = 100 # core to agg
        lvl2_bw = 40 # agg to edge
        lvl3_bw = 10 # edge to host <BOTTLENECK> 

        # LATENCY
        lvl1_delay = '30ms' # core to agg
        lvl2_delay = '20ms' # agg to edge
        lvl3_delay = '10ms' # edge to host

        #Start to build the topology here

        # define all the hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')

        # DEFINING SWITCHES (4 edge-switches, 2 agg-switches, 1 core-switch)
        e1 = self.addSwitch('e1')
        e2 = self.addSwitch('e2')
        e3 = self.addSwitch('e3')
        e4 = self.addSwitch('e4')

        a1 = self.addSwitch('a1')
        a2 = self.addSwitch('a2')

        c1 = self.addSwitch('c1')

        # DEFINING LINKS...
        # links between each host and the switches
        self.addLink(h1, e1, bw=lvl3_bw, delay=lvl3_delay) # 
        self.addLink(h2, e1, bw=lvl3_bw, delay=lvl3_delay) #
        self.addLink(h3, e2, bw=lvl3_bw, delay=lvl3_delay) #
        self.addLink(h4, e2, bw=lvl3_bw, delay=lvl3_delay) # 
        self.addLink(h5, e3, bw=lvl3_bw, delay=lvl3_delay) #
        self.addLink(h6, e3, bw=lvl3_bw, delay=lvl3_delay) #
        self.addLink(h7, e4, bw=lvl3_bw, delay=lvl3_delay) #
        self.addLink(h8, e4, bw=lvl3_bw, delay=lvl3_delay) #


        # links between switches, with bandwidth (Mbps) and delay (ms)
        self.addLink(e1, a1, bw=lvl2_bw, delay=lvl2_delay) # agg to edge // lvl 2
        self.addLink(e2, a1, bw=lvl2_bw, delay=lvl2_delay) # agg to edge // lvl 2
        self.addLink(e3, a2, bw=lvl2_bw, delay=lvl2_delay) # agg to edge // lvl 2
        self.addLink(e4, a2, bw=lvl2_bw, delay=lvl2_delay) # agg to edge // lvl 2

        self.addLink(a1, c1, bw=lvl1_bw, delay=lvl1_delay) # agg to edge // lvl 1
        self.addLink(a2, c1, bw=lvl1_bw, delay=lvl1_delay) # agg to edge // lvl 1





       
 
        
if __name__ == '__main__':
    setLogLevel( 'info' )

    topo = AssignmentNetworks()
    # net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,autoStaticArp=True)
    net = Mininet(controller=RemoteController, topo=topo, link=TCLink, autoSetMacs=True,autoStaticArp=True)

    # Run network
    net.start()
    CLI( net )
    net.stop()

