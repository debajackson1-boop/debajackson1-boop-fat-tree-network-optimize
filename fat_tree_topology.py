#!/usr/bin/env python3
"""
fat_tree_topology.py
Fat-Tree network topology definition
"""

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import Controller, OVSSwitch
from router_config import LinuxRouter

class FatTreeTopology:
    """Fat-Tree topology builder"""
    
    def __init__(self):
        self.net = None
        self.nodes = {}
    
    def create_network(self):
        """Create the Fat-Tree network topology"""
        print("🏗️ Creating Fat-Tree topology...")
        
        # Initialize Mininet
        self.net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)
        self.net.addController('c0')
        
        # Create layers
        self._create_core_layer()
        self._create_aggregation_layer()
        self._create_edge_layer()
        self._create_hosts()
        
        # Create links
        self._create_core_aggregation_links()
        self._create_aggregation_edge_links()
        self._create_host_links()
        
        print("✅ Fat-Tree topology created")
        return self.net
    
    def _create_core_layer(self):
        """Create core routers"""
        print("   Creating core layer...")
        self.nodes['cr1'] = self.net.addHost('cr1', cls=LinuxRouter, ip=None)
        self.nodes['cr2'] = self.net.addHost('cr2', cls=LinuxRouter, ip=None)
    
    def _create_aggregation_layer(self):
        """Create aggregation routers"""
        print("   Creating aggregation layer...")
        self.nodes['ar1'] = self.net.addHost('ar1', cls=LinuxRouter, ip=None)
        self.nodes['ar2'] = self.net.addHost('ar2', cls=LinuxRouter, ip=None)
        self.nodes['ar3'] = self.net.addHost('ar3', cls=LinuxRouter, ip=None)
        self.nodes['ar4'] = self.net.addHost('ar4', cls=LinuxRouter, ip=None)
    
    def _create_edge_layer(self):
        """Create edge switches"""
        print("   Creating edge layer...")
        self.nodes['es1'] = self.net.addSwitch('es1')
        self.nodes['es2'] = self.net.addSwitch('es2')
        self.nodes['es3'] = self.net.addSwitch('es3')
        self.nodes['es4'] = self.net.addSwitch('es4')
    
    def _create_hosts(self):
        """Create hosts"""
        print("   Creating hosts...")
        # Pod 1 hosts
        self.nodes['h1'] = self.net.addHost('h1', ip='10.1.1.1/24')
        self.nodes['h2'] = self.net.addHost('h2', ip='10.1.1.2/24')
        self.nodes['h3'] = self.net.addHost('h3', ip='10.1.2.1/24')
        self.nodes['h4'] = self.net.addHost('h4', ip='10.1.2.2/24')
        
        # Pod 2 hosts
        self.nodes['h5'] = self.net.addHost('h5', ip='10.2.1.1/24')
        self.nodes['h6'] = self.net.addHost('h6', ip='10.2.1.2/24')
        self.nodes['h7'] = self.net.addHost('h7', ip='10.2.2.1/24')
        self.nodes['h8'] = self.net.addHost('h8', ip='10.2.2.2/24')
    
    def _create_core_aggregation_links(self):
        """Create core-aggregation links"""
        print("   Creating core-aggregation links...")
        
        # Core 1 to aggregation
        self.net.addLink(
            self.nodes['cr1'], self.nodes['ar1'],
            intfName1='cr1-eth0', intfName2='ar1-eth0',
            params1={'ip': '172.16.1.1/30'}, 
            params2={'ip': '172.16.1.2/30'}
        )
        
        self.net.addLink(
            self.nodes['cr1'], self.nodes['ar3'],
            intfName1='cr1-eth2', intfName2='ar3-eth0',
            params1={'ip': '172.16.3.1/30'}, 
            params2={'ip': '172.16.3.2/30'}
        )
        
        # Core 2 to aggregation
        self.net.addLink(
            self.nodes['cr2'], self.nodes['ar2'],
            intfName1='cr2-eth1', intfName2='ar2-eth1',
            params1={'ip': '172.16.6.1/30'}, 
            params2={'ip': '172.16.6.2/30'}
        )
        
        self.net.addLink(
            self.nodes['cr2'], self.nodes['ar4'],
            intfName1='cr2-eth3', intfName2='ar4-eth1',
            params1={'ip': '172.16.8.1/30'}, 
            params2={'ip': '172.16.8.2/30'}
        )
    
    def _create_aggregation_edge_links(self):
        """Create aggregation-edge links"""
        print("   Creating aggregation-edge links...")
        
        # Straight links (primary)
        self.net.addLink(
            self.nodes['ar1'], self.nodes['es1'],
            intfName1='ar1-eth2', 
            params1={'ip': '10.1.1.254/24'}
        )
        
        self.net.addLink(
            self.nodes['ar2'], self.nodes['es2'],
            intfName1='ar2-eth2', 
            params1={'ip': '10.1.2.254/24'}
        )
        
        self.net.addLink(
            self.nodes['ar3'], self.nodes['es3'],
            intfName1='ar3-eth2', 
            params1={'ip': '10.2.1.254/24'}
        )
        
        self.net.addLink(
            self.nodes['ar4'], self.nodes['es4'],
            intfName1='ar4-eth2', 
            params1={'ip': '10.2.2.254/24'}
        )
        
        # Diagonal links (backup)
        self.net.addLink(
            self.nodes['ar1'], self.nodes['es2'],
            intfName1='ar1-eth3', 
            params1={'ip': '10.1.2.253/24'}
        )
        
        self.net.addLink(
            self.nodes['ar2'], self.nodes['es1'],
            intfName1='ar2-eth3', 
            params1={'ip': '10.1.1.253/24'}
        )
        
        self.net.addLink(
            self.nodes['ar3'], self.nodes['es4'],
            intfName1='ar3-eth3', 
            params1={'ip': '10.2.2.253/24'}
        )
        
        self.net.addLink(
            self.nodes['ar4'], self.nodes['es3'],
            intfName1='ar4-eth3', 
            params1={'ip': '10.2.1.253/24'}
        )
    
    def _create_host_links(self):
        """Create host-switch links"""
        print("   Creating host links...")
        
        # Pod 1 hosts
        self.net.addLink(self.nodes['h1'], self.nodes['es1'])
        self.net.addLink(self.nodes['h2'], self.nodes['es1'])
        self.net.addLink(self.nodes['h3'], self.nodes['es2'])
        self.net.addLink(self.nodes['h4'], self.nodes['es2'])
        
        # Pod 2 hosts
        self.net.addLink(self.nodes['h5'], self.nodes['es3'])
        self.net.addLink(self.nodes['h6'], self.nodes['es3'])
        self.net.addLink(self.nodes['h7'], self.nodes['es4'])
        self.net.addLink(self.nodes['h8'], self.nodes['es4'])
    
    def get_topology_info(self):
        """Get topology information"""
        return {
            'pods': {
                'pod1': {
                    'subnets': ['10.1.1.0/24', '10.1.2.0/24'],
                    'hosts': ['h1', 'h2', 'h3', 'h4'],
                    'routers': ['ar1', 'ar2'],
                    'switches': ['es1', 'es2'],
                    'core': 'cr1'
                },
                'pod2': {
                    'subnets': ['10.2.1.0/24', '10.2.2.0/24'],
                    'hosts': ['h5', 'h6', 'h7', 'h8'],
                    'routers': ['ar3', 'ar4'],
                    'switches': ['es3', 'es4'],
                    'core': 'cr2'
                }
            },
            'links': {
                'straight': [
                    ('ar1', 'es1'), ('ar2', 'es2'),
                    ('ar3', 'es3'), ('ar4', 'es4')
                ],
                'diagonal': [
                    ('ar1', 'es2'), ('ar2', 'es1'),
                    ('ar3', 'es4'), ('ar4', 'es3')
                ],
                'core': [
                    ('cr1', 'ar1'), ('cr1', 'ar3'),
                    ('cr2', 'ar2'), ('cr2', 'ar4')
                ]
            }
        }

def create_fat_tree():
    """Convenience function to create Fat-Tree topology"""
    topology = FatTreeTopology()
    return topology.create_network(), topology.get_topology_info()
