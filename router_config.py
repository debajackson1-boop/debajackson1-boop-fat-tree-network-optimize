#!/usr/bin/env python3
"""
router_config.py
Router and switch configuration utilities
"""

from mininet.node import Node

class LinuxRouter(Node):
    """Linux router with IP forwarding enabled"""
    
    def config(self, **params):
        super().config(**params)
        # Enable IP forwarding
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        
        # Disable IPv6 to avoid interference
        self.cmd('sysctl -w net.ipv6.conf.all.disable_ipv6=1')
        
        # Optimize for better performance
        self.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0')
        self.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0')
    
    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()

class RouterConfigManager:
    """Manages router configurations and routing tables"""
    
    def __init__(self, net):
        self.net = net
    
    def setup_basic_routing(self):
        """Setup basic routing for all routers and hosts"""
        print("🔧 Setting up basic routing...")
        
        # Setup host default routes
        self._setup_host_routes()
        
        # Setup switch forwarding
        self._setup_switch_forwarding()
        
        # Setup router routes
        self._setup_router_routes()
        
        # Setup core routing
        self._setup_core_routing()
        
        print("✅ Basic routing setup complete")
    
    def _setup_host_routes(self):
        """Setup default routes for all hosts"""
        host_routes = {
            'h1': '10.1.1.254',  # ar1
            'h2': '10.1.1.254',  # ar1
            'h3': '10.1.2.254',  # ar2
            'h4': '10.1.2.254',  # ar2
            'h5': '10.2.1.254',  # ar3
            'h6': '10.2.1.254',  # ar3
            'h7': '10.2.2.254',  # ar4
            'h8': '10.2.2.254'   # ar4
        }
        
        for host_name, gateway in host_routes.items():
            host = self.net.get(host_name)
            if host:
                host.cmd(f'ip route add default via {gateway}')
    
    def _setup_switch_forwarding(self):
        """Setup switch forwarding rules"""
        switches = ['es1', 'es2', 'es3', 'es4']
        
        for switch_name in switches:
            switch = self.net.get(switch_name)
            if switch:
                # Clear existing flows
                switch.cmd(f'ovs-ofctl del-flows {switch_name}')
                # Add normal forwarding flow
                switch.cmd(f'ovs-ofctl add-flow {switch_name} "priority=0,actions=normal"')
    
    def _setup_router_routes(self):
        """Setup aggregation router routes"""
        # Pod 1 routers
        ar1 = self.net.get('ar1')
        if ar1:
            # Route to other subnet in same pod via diagonal
            ar1.cmd('ip route add 10.1.2.0/24 dev ar1-eth3 metric 1')
            # Route to other pods via core
            ar1.cmd('ip route add 10.2.0.0/16 via 172.16.1.1')
        
        ar2 = self.net.get('ar2')
        if ar2:
            # Route to other subnet in same pod via diagonal
            ar2.cmd('ip route add 10.1.1.0/24 dev ar2-eth3 metric 1')
            # Route to other pods via core
            ar2.cmd('ip route add 10.2.0.0/16 via 172.16.6.1')
        
        # Pod 2 routers
        ar3 = self.net.get('ar3')
        if ar3:
            # Route to other subnet in same pod via diagonal
            ar3.cmd('ip route add 10.2.2.0/24 dev ar3-eth3 metric 1')
            # Route to other pods via core
            ar3.cmd('ip route add 10.1.0.0/16 via 172.16.3.1')
        
        ar4 = self.net.get('ar4')
        if ar4:
            # Route to other subnet in same pod via diagonal
            ar4.cmd('ip route add 10.2.1.0/24 dev ar4-eth3 metric 1')
            # Route to other pods via core
            ar4.cmd('ip route add 10.1.0.0/16 via 172.16.8.1')
    
    def _setup_core_routing(self):
        """Setup core router routes"""
        cr1 = self.net.get('cr1')
        if cr1:
            # Routes to Pod 1 via ar1
            cr1.cmd('ip route add 10.1.1.0/24 via 172.16.1.2')
            cr1.cmd('ip route add 10.1.2.0/24 via 172.16.1.2')
            # Routes to Pod 2 via ar3
            cr1.cmd('ip route add 10.2.1.0/24 via 172.16.3.2')
            cr1.cmd('ip route add 10.2.2.0/24 via 172.16.3.2')
        
        cr2 = self.net.get('cr2')
        if cr2:
            # Routes to Pod 1 via ar2
            cr2.cmd('ip route add 10.1.1.0/24 via 172.16.6.2')
            cr2.cmd('ip route add 10.1.2.0/24 via 172.16.6.2')
            # Routes to Pod 2 via ar4
            cr2.cmd('ip route add 10.2.1.0/24 via 172.16.8.2')
            cr2.cmd('ip route add 10.2.2.0/24 via 172.16.8.2')
    
    def clear_routes(self, subnet_pairs):
        """Clear routes for specific subnet pairs"""
        for src_subnet, dst_subnet in subnet_pairs:
            for router_name in ['ar1', 'ar2', 'ar3', 'ar4']:
                router = self.net.get(router_name)
                if router:
                    router.cmd(f'ip route del {src_subnet} 2>/dev/null || true')
                    router.cmd(f'ip route del {dst_subnet} 2>/dev/null || true')
                    router.cmd('ip route flush cache')
    
    def update_router_route(self, router_name, destination, route_config):
        """Update a specific router route - FIXED to avoid duplicates"""
        router = self.net.get(router_name)
        if not router:
            return False
        
        # CRITICAL FIX: Clear ALL existing routes to this destination
        router.cmd(f'ip route del {destination} 2>/dev/null || true')
        # Also clear any duplicates with different metrics
        router.cmd(f'ip route del {destination} metric 1 2>/dev/null || true')
        router.cmd(f'ip route del {destination} metric 2 2>/dev/null || true')
        
        # Add new route
        if route_config['type'] == 'dev':
            router.cmd(f'ip route add {destination} dev {route_config["interface"]} metric {route_config.get("metric", 1)}')
        elif route_config['type'] == 'via':
            router.cmd(f'ip route add {destination} via {route_config["gateway"]} metric {route_config.get("metric", 1)}')
        
        router.cmd('ip route flush cache')
        return True
    
    def update_host_route(self, host_name, destination, gateway):
        """Update a specific host route"""
        host = self.net.get(host_name)
        if not host:
            return False
        
        # Clear existing route
        host.cmd(f'ip route del {destination} 2>/dev/null || true')
        
        # Add new route
        host.cmd(f'ip route add {destination} via {gateway} metric 1')
        host.cmd('ip route flush cache')
        return True
    
    def show_routing_table(self, node_name):
        """Show routing table for a specific node"""
        node = self.net.get(node_name)
        if node:
            print(f"📋 {node_name} routing table:")
            routes = node.cmd('ip route show')
            for line in routes.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Node {node_name} not found")
    
    def show_interface_status(self, node_name):
        """Show interface status for a specific node"""
        node = self.net.get(node_name)
        if node:
            print(f"📋 {node_name} interfaces:")
            interfaces = node.cmd('ip link show')
            for line in interfaces.strip().split('\n'):
                if 'eth' in line or 'lo' in line:
                    print(f"   {line}")
        else:
            print(f"❌ Node {node_name} not found")
    
    def test_connectivity(self, src_name, dst_name):
        """Test connectivity between two nodes"""
        src = self.net.get(src_name)
        dst = self.net.get(dst_name)
        
        if not src or not dst:
            return False
        
        result = src.cmd(f'ping -c 1 -W 2 {dst.IP()}')
        return 'bytes from' in result
    
    def get_node_subnet(self, node_name):
        """Get subnet for a node"""
        node = self.net.get(node_name)
        if node:
            ip = node.IP()
            if ip:
                return ip[:ip.rfind('.')] + '.0/24'
        return None
