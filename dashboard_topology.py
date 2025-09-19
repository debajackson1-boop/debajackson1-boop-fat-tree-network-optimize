#!/usr/bin/env python3
"""
dashboard_topology.py
Dynamic topology generation and analysis
"""

from dashboard_utils import get_controller_data

def analyze_network_from_links(links):
    """Analyze network structure from link data - truly dynamic without hardcoding"""
    nodes = set()
    connections = []
    
    # Extract nodes and connections from actual link data
    for link_name, status in links.items():
        if '↔' in link_name:
            node1, node2 = link_name.split('↔')
            nodes.add(node1)
            nodes.add(node2)
            connections.append({
                'from': node1,
                'to': node2,
                'status': status,
                'name': link_name
            })
    
    # Categorize nodes dynamically based on naming convention
    node_categories = {
        'core': sorted([n for n in nodes if n.startswith('cr')]),
        'aggregation': sorted([n for n in nodes if n.startswith('ar')]),
        'edge': sorted([n for n in nodes if n.startswith('es')]),
        'hosts': sorted([n for n in nodes if n.startswith('h')])
    }
    
    print(f"🔍 Dashboard detected nodes from links: {dict((k, len(v)) for k, v in node_categories.items())}")
    
    return node_categories, connections

def get_all_network_nodes_from_controller():
    """Get complete node list from controller if available - no hardcoding"""
    try:
        # Check if we can get more complete data from controller
        connected, data = get_controller_data()
        if connected and 'data' in data:
            # Look for additional node information in controller data
            controller_data = data['data']
            
            # Check if controller provides complete node list
            if 'all_nodes' in controller_data:
                return controller_data['all_nodes']
            
            # Try to infer from connectivity data
            if 'connectivity' in controller_data:
                all_nodes = set()
                for conn_name in controller_data['connectivity'].keys():
                    if '-' in conn_name:
                        node1, node2 = conn_name.split('-')
                        all_nodes.add(node1)
                        all_nodes.add(node2)
                
                if all_nodes:
                    categorized = {
                        'core': sorted([n for n in all_nodes if n.startswith('cr')]),
                        'aggregation': sorted([n for n in all_nodes if n.startswith('ar')]),
                        'edge': sorted([n for n in all_nodes if n.startswith('es')]),
                        'hosts': sorted([n for n in all_nodes if n.startswith('h')])
                    }
                    print(f"🔍 Dashboard found additional nodes from connectivity: {dict((k, len(v)) for k, v in categorized.items())}")
                    return categorized
        
        return None
    except Exception as e:
        print(f"🔍 Could not get additional nodes from controller: {e}")
        return None

def get_missing_host_connections(nodes, connections):
    """Dynamically determine missing host connections - no hardcoding"""
    hosts = nodes.get('hosts', [])
    edge_switches = nodes.get('edge', [])
    
    # Extract existing connections
    existing_connections = set()
    for conn in connections:
        existing_connections.add((conn['from'], conn['to']))
        existing_connections.add((conn['to'], conn['from']))
    
    missing_connections = []
    
    if hosts and edge_switches:
        # Dynamic mapping: distribute hosts evenly among edge switches
        sorted_hosts = sorted(hosts)
        sorted_switches = sorted(edge_switches)
        hosts_per_switch = max(1, len(sorted_hosts) // len(sorted_switches))
        
        for i, host in enumerate(sorted_hosts):
            # Determine which switch this host should connect to
            switch_index = min(i // hosts_per_switch, len(sorted_switches) - 1)
            switch = sorted_switches[switch_index]
            
            # Check if connection already exists
            if (host, switch) not in existing_connections:
                missing_connections.append({
                    'from': host,
                    'to': switch,
                    'status': True,  # Assume host connections are up
                    'name': f'{host}↔{switch}'
                })
    
    if missing_connections:
        print(f"🔍 Dashboard adding {len(missing_connections)} missing host connections (dynamic distribution)")
    return missing_connections

def generate_topology_svg(nodes, connections):
    """Generate topology SVG dynamically based on actual network data"""
    # Add missing host connections dynamically
    missing_host_connections = get_missing_host_connections(nodes, connections)
    all_connections = connections + missing_host_connections
    
    # If we have no nodes at all, show a message
    total_nodes = sum(len(node_list) for node_list in nodes.values())
    if total_nodes == 0:
        return '<text x="500" y="300" text-anchor="middle" fill="white" font-size="16">No network data available</text>'
    
    # Calculate positions dynamically
    positions = {}
    svg_width = 1000
    margin = 80
    
    # Dynamic layer positioning based on what layers exist
    available_layers = [layer for layer, node_list in nodes.items() if node_list]
    layer_spacing = 140
    start_y = 80
    
    layer_positions = {}
    for i, layer in enumerate(['core', 'aggregation', 'edge', 'hosts']):
        if layer in available_layers:
            layer_positions[layer] = start_y + (i * layer_spacing)
    
    # Calculate node positions for each layer
    for layer, node_list in nodes.items():
        if not node_list:
            continue
        
        node_list = sorted(node_list)
        count = len(node_list)
        
        if layer == 'hosts' and 'edge' in nodes and nodes['edge']:
            # Dynamic host positioning: group hosts under their connected switches
            edge_switches = sorted(nodes['edge'])
            
            # Find which hosts connect to which switches
            host_to_switch = {}
            for conn in all_connections:
                if conn['from'].startswith('h') and conn['to'].startswith('es'):
                    host_to_switch[conn['from']] = conn['to']
                elif conn['to'].startswith('h') and conn['from'].startswith('es'):
                    host_to_switch[conn['to']] = conn['from']
            
            # Position hosts based on their switch connections
            for host in node_list:
                if host in host_to_switch:
                    connected_switch = host_to_switch[host]
                    if connected_switch in positions:
                        switch_x, _ = positions[connected_switch]
                        # Get other hosts connected to same switch
                        same_switch_hosts = [h for h, s in host_to_switch.items() if s == connected_switch]
                        same_switch_hosts = sorted(same_switch_hosts)
                        
                        if len(same_switch_hosts) == 1:
                            host_x = switch_x
                        else:
                            # Position multiple hosts around their switch
                            host_index = same_switch_hosts.index(host)
                            offset = (host_index - (len(same_switch_hosts) - 1) / 2) * 40
                            host_x = switch_x + offset
                        
                        positions[host] = (host_x, layer_positions[layer])
                
                # Fallback positioning for unconnected hosts
                if host not in positions:
                    # Use even distribution as fallback
                    host_index = node_list.index(host)
                    if count == 1:
                        x_pos = svg_width // 2
                    else:
                        available_width = svg_width - (2 * margin)
                        spacing = available_width / (count - 1)
                        x_pos = margin + host_index * spacing
                    positions[host] = (x_pos, layer_positions[layer])
        else:
            # Standard positioning for non-host layers
            if count == 1:
                x_positions = [svg_width // 2]
            else:
                available_width = svg_width - (2 * margin)
                spacing = available_width / (count - 1) if count > 1 else 0
                x_positions = [margin + i * spacing for i in range(count)]
            
            for i, node in enumerate(node_list):
                positions[node] = (x_positions[i], layer_positions[layer])
    
    # Generate SVG with dynamic content
    svg_parts = []
    
    # Dynamic title based on what's actually present
    node_counts = {layer: len(nodes.get(layer, [])) for layer in ['core', 'aggregation', 'edge', 'hosts']}
    present_layers = [layer for layer, count in node_counts.items() if count > 0]
    
    svg_parts.append(f'''
        <defs>
            <style>
                .node-core {{ fill: #FF9800; stroke: #EF6C00; stroke-width: 3; }}
                .node-aggregation {{ fill: #2196F3; stroke: #1565C0; stroke-width: 2; }}
                .node-edge {{ fill: #9C27B0; stroke: #7B1FA2; stroke-width: 2; }}
                .node-hosts {{ fill: #4CAF50; stroke: #2E7D32; stroke-width: 2; }}
                .link-up {{ stroke: #4CAF50; stroke-width: 2; opacity: 0.8; }}
                .link-down {{ stroke: #F44336; stroke-width: 2; stroke-dasharray: 8,4; opacity: 0.9; animation: dash 2s linear infinite; }}
                .link-host {{ stroke: #4CAF50; stroke-width: 1.5; opacity: 0.6; }}
                .node-label {{ fill: white; font-size: 11px; font-weight: bold; text-anchor: middle; }}
                @keyframes dash {{ to {{ stroke-dashoffset: -12; }} }}
            </style>
        </defs>
        <rect width="100%" height="100%" fill="rgba(0,0,0,0.1)"/>
        <text x="{svg_width//2}" y="30" text-anchor="middle" fill="white" font-size="18" font-weight="bold">
            🌐 Network Topology
        </text>
        <text x="{svg_width//2}" y="50" text-anchor="middle" fill="white" font-size="12" opacity="0.8">
            Layers: {' • '.join(present_layers).title()}
        </text>
    ''')
    
    # Draw all connections
    for conn in all_connections:
        from_node = conn['from']
        to_node = conn['to']
        
        if from_node in positions and to_node in positions:
            x1, y1 = positions[from_node]
            x2, y2 = positions[to_node]
            
            # Dynamic node radius calculation
            def get_node_radius(node):
                if node.startswith('cr'): return 25
                elif node.startswith('ar'): return 22
                elif node.startswith('es'): return 20
                elif node.startswith('h'): return 15
                else: return 18
            
            radius = max(get_node_radius(from_node), get_node_radius(to_node))
            
            # Adjust line endpoints
            if y1 < y2:
                y1 += radius
                y2 -= radius
            elif y1 > y2:
                y1 -= radius
                y2 += radius
            
            # Determine link class
            if from_node.startswith('h') or to_node.startswith('h'):
                link_class = 'link-host'
            else:
                link_class = 'link-up' if conn['status'] else 'link-down'
            
            svg_parts.append(f'''
                <line class="{link_class}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">
                    <title>{conn['name']} - {'UP' if conn['status'] else 'DOWN'}</title>
                </line>
            ''')
    
    # Dynamic layer labels
    layer_info = {
        'core': {'color': '#FF9800', 'name': 'Core'},
        'aggregation': {'color': '#2196F3', 'name': 'Aggregation'},
        'edge': {'color': '#9C27B0', 'name': 'Edge'},
        'hosts': {'color': '#4CAF50', 'name': 'Hosts'}
    }
    
    for layer, node_list in nodes.items():
        if node_list and layer in layer_positions:
            y = layer_positions[layer] - 25
            count = len(node_list)
            layer_name = layer_info[layer]['name']
            color = layer_info[layer]['color']
            
            svg_parts.append(f'''
                <text x="50" y="{y}" text-anchor="start" fill="{color}" 
                      font-size="12" font-weight="bold">{layer_name} ({count})</text>
            ''')
    
    # Draw nodes dynamically
    for layer, node_list in nodes.items():
        for node in node_list:
            if node in positions:
                x, y = positions[node]
                
                if layer == 'edge':
                    # Rectangles for switches
                    svg_parts.append(f'''
                        <rect class="node-{layer}" x="{x-20}" y="{y-12}" width="40" height="24" rx="4"/>
                        <text class="node-label" x="{x}" y="{y+3}">{node.upper()}</text>
                    ''')
                else:
                    # Circles for other node types
                    if layer == 'core':
                        radius = 25
                        font_size = 12
                    elif layer == 'aggregation':
                        radius = 22
                        font_size = 11
                    elif layer == 'hosts':
                        radius = 15
                        font_size = 10
                    else:
                        radius = 18
                        font_size = 11
                    
                    svg_parts.append(f'''
                        <circle class="node-{layer}" cx="{x}" cy="{y}" r="{radius}"/>
                        <text class="node-label" x="{x}" y="{y+3}" font-size="{font_size}">{node.upper()}</text>
                    ''')
    
    # Dynamic statistics
    infrastructure_links = [c for c in all_connections if not (c['from'].startswith('h') or c['to'].startswith('h'))]
    total_infra_links = len(infrastructure_links)
    up_infra_links = sum(1 for c in infrastructure_links if c['status'])
    health = int((up_infra_links / total_infra_links * 100)) if total_infra_links > 0 else 100
    
    total_nodes = sum(len(node_list) for node_list in nodes.values())
    
    svg_parts.append(f'''
        <g>
            <text x="50" y="540" fill="white" font-size="12" font-weight="bold">
                Infrastructure Health: {up_infra_links}/{total_infra_links} links UP ({health}%)
            </text>
            <text x="50" y="560" fill="white" font-size="10">
                🟢 UP Links  🔴 DOWN Links  🟢 Host Connections
            </text>
            <text x="50" y="580" fill="white" font-size="10">
                Total Nodes: {total_nodes} • Infrastructure Links: {total_infra_links} • Host Connections: {len(all_connections) - total_infra_links}
            </text>
        </g>
    ''')
    
    return ''.join(svg_parts)
