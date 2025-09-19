#!/usr/bin/env python3
"""
working_dashboard.py
Dashboard that properly communicates with the controller for command execution
"""

from flask import Flask, jsonify, render_template_string, request
import json
import time
import os
import subprocess
import threading

app = Flask(__name__)

def get_controller_data():
    """Get data from controller status file"""
    try:
        status_files = ['/tmp/fat_tree_status.json', '/var/tmp/fat_tree_status.json', './fat_tree_status.json']
        
        for file_path in status_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                file_age = time.time() - data.get('timestamp', 0)
                if file_age < 60:
                    return True, data
        
        return False, {}
    except Exception as e:
        print(f"Error reading controller data: {e}")
        return False, {}

def execute_command_via_controller(command):
    """Execute command by communicating with the main controller"""
    try:
        print(f"🔧 Dashboard sending command to controller: '{command}'")
        
        # Create command request file for controller
        cmd_request_file = '/tmp/dashboard_command_request.json'
        cmd_response_file = '/tmp/dashboard_command_response.json'
        
        # Clean up any old response file
        if os.path.exists(cmd_response_file):
            os.remove(cmd_response_file)
        
        # Write command request
        request_data = {
            'command': command,
            'timestamp': time.time(),
            'source': 'dashboard'
        }
        
        with open(cmd_request_file, 'w') as f:
            json.dump(request_data, f)
        
        print(f"   📤 Command request written to {cmd_request_file}")
        
        # Wait for controller to process and respond
        max_wait = 15  # seconds
        wait_interval = 0.5
        waited = 0
        
        while waited < max_wait:
            if os.path.exists(cmd_response_file):
                try:
                    with open(cmd_response_file, 'r') as f:
                        response_data = json.load(f)
                    
                    # Clean up files
                    try:
                        os.remove(cmd_request_file)
                        os.remove(cmd_response_file)
                    except:
                        pass
                    
                    success = response_data.get('success', False)
                    output = response_data.get('output', response_data.get('error', 'No output'))
                    
                    print(f"   📥 Received response: success={success}, output_len={len(output)}")
                    return success, output
                    
                except Exception as e:
                    print(f"   ❌ Error reading response: {e}")
                    break
            
            time.sleep(wait_interval)
            waited += wait_interval
        
        # Timeout - try to clean up request file
        try:
            if os.path.exists(cmd_request_file):
                os.remove(cmd_request_file)
        except:
            pass
        
        return False, f"Controller did not respond within {max_wait} seconds. Make sure the main controller is running and monitoring for dashboard commands."
        
    except Exception as e:
        error_msg = f"Error communicating with controller: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def execute_command(command):
    """Execute command with proper controller communication"""
    try:
        print(f"🔧 Dashboard executing command: '{command}'")
        
        if not command.strip():
            return False, "No command provided"
        
        # Handle help command locally (no need for controller)
        if command in ['help', 'h']:
            help_text = """🌐 Available Dashboard Commands:
=====================================

🏓 CONNECTIVITY TESTING:
• h1 ping h5          - Test connectivity between hosts
• h3 ping h7          - Test cross-pod connectivity
• h2 ping h6          - Test another connection

🔗 LINK MANAGEMENT:
• link ar1 es1 down   - Bring link down (break connection)
• link ar1 es1 up     - Bring link up (restore connection)
• link cr1 ar1 down   - Break core link
• links               - Show all link status

🎛️ CONTROLLER METHODS:
• py net.controller.auto_detect_and_fix_failures()
• py net.controller.reset_to_clean_state()
• py net.controller.break_link_and_auto_fix('ar1', 'es1')

📊 STATUS COMMANDS:
• status              - Show controller and network status
• links               - Show all link states

💡 EXAMPLE WORKFLOW:
1. status                             (check system status)
2. h1 ping h5                         (test connectivity)
3. link ar1 es1 down                  (break a link)
4. h1 ping h5                         (test broken connectivity)
5. py net.controller.auto_detect_and_fix_failures()
6. h1 ping h5                         (test if fixed)

⚠️ Note: All commands are processed by the main controller.
Make sure it's running in another terminal!"""
            return True, help_text
        
        # Handle status command locally
        elif command in ['status', 'show']:
            try:
                connected, data = get_controller_data()
                if connected:
                    status_info = []
                    status_info.append(f"🟢 Controller Status: CONNECTED")
                    status_info.append(f"📊 PID: {data.get('pid', 'Unknown')}")
                    status_info.append(f"⏰ Last Update: {time.strftime('%H:%M:%S', time.localtime(data.get('timestamp', 0)))}")
                    
                    if 'data' in data and data['data'].get('health'):
                        health = data['data']['health']
                        status_info.append(f"🔗 Link Health: {health.get('link_health', '?')}%")
                        status_info.append(f"🌐 Connectivity: {health.get('connectivity_health', '?')}%")
                        status_info.append(f"📈 Overall: {health.get('overall_status', 'Unknown')}")
                    
                    status_info.append(f"\n💡 The controller is responding and ready for commands!")
                    return True, '\n'.join(status_info)
                else:
                    return False, "🔴 Controller Status: DISCONNECTED\n\nTo fix this:\n1. Make sure you're running the main controller\n2. Check if the controller script is active\n3. Look for fat_tree_status.json file"
            except Exception as e:
                return False, f"Error getting status: {str(e)}"
        
        # For all other commands, send to controller
        else:
            return execute_command_via_controller(command)
            
    except Exception as e:
        error_msg = f"Command execution error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

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

# HTML Template with improved UI feedback
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fat-Tree Network Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .dashboard-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .section-title {
            font-size: 1.4em;
            margin-bottom: 15px;
            color: #4CAF50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .topology-container {
            grid-column: 1 / -1;
            text-align: center;
        }
        
        .status-indicator {
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin: 10px;
            font-weight: bold;
        }
        
        .status-connected {
            background: rgba(76, 175, 80, 0.2);
            border: 2px solid #4CAF50;
            color: #4CAF50;
        }
        
        .status-disconnected {
            background: rgba(244, 67, 54, 0.2);
            border: 2px solid #F44336;
            color: #F44336;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .command-section {
            grid-column: 1 / -1;
        }
        
        .command-input {
            width: 70%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-family: monospace;
            font-size: 14px;
        }
        
        .command-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #45a049;
            transform: translateY(-2px);
        }
        
        .btn.danger { background: #F44336; }
        .btn.warning { background: #FF9800; }
        .btn.info { background: #2196F3; }
        
        .btn:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
        }
        
        .command-output {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            font-family: monospace;
            font-size: 13px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        
        .log-entry {
            margin: 5px 0;
            padding: 8px;
            border-radius: 3px;
            border-left: 4px solid transparent;
        }
        
        .log-success { 
            background: rgba(76, 175, 80, 0.2); 
            border-left-color: #4CAF50;
        }
        .log-error { 
            background: rgba(244, 67, 54, 0.2); 
            border-left-color: #F44336;
        }
        .log-info {
            background: rgba(33, 150, 243, 0.2);
            border-left-color: #2196F3;
        }
        
        .loading {
            opacity: 0.6;
        }
        
        .link-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .link-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }
        
        .link-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .link-up { background: #4CAF50; }
        .link-down { background: #F44336; }
        
        @media (max-width: 768px) {
            .dashboard-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Fat-Tree Network Dashboard</h1>
            <div id="connection-status" class="status-indicator">
                🔄 Checking connection...
            </div>
            <p>Real-time monitoring and control via controller communication</p>
        </div>

        <div class="dashboard-grid">
            <!-- Network Overview -->
            <div class="dashboard-section">
                <div class="section-title">📊 Network Overview</div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="total-nodes">--</div>
                        <div>Total Nodes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="total-links">--</div>
                        <div>Total Links</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="link-health">--</div>
                        <div>Link Health</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="connectivity">--</div>
                        <div>Connectivity</div>
                    </div>
                </div>
            </div>

            <!-- Link Status -->
            <div class="dashboard-section">
                <div class="section-title">🔗 Link Status</div>
                <div class="link-status" id="link-status">
                    Loading...
                </div>
            </div>
        </div>




        <!-- Network Topology -->
        <div class="dashboard-section topology-container">
            <div class="section-title">🏗️ Network Topology</div>
            <svg width="100%" height="600" viewBox="0 0 1000 600" id="topology-svg">
                <text x="500" y="300" text-anchor="middle" fill="white">Loading topology...</text>
            </svg>
        </div>

        <!-- Command Interface -->
        <div class="dashboard-section command-section">
            <div class="section-title">💻 Network Commands</div>
            <div style="margin-bottom: 15px;">
                <input type="text" id="command-input" class="command-input" 
                       placeholder="Enter command (e.g., h1 ping h5, help, status)" 
                       onkeypress="handleEnter(event)">
                <button class="btn" id="execute-btn" onclick="executeCommand()">Execute</button>
                <button class="btn info" onclick="insertCommand('help')">Help</button>
                <button class="btn info" onclick="insertCommand('status')">Status</button>
                <button class="btn" onclick="insertCommand('h1 ping h5')">Test Ping</button>
                <button class="btn warning" onclick="insertCommand('py net.controller.auto_detect_and_fix_failures()')">Auto-Fix</button>
                <button class="btn danger" onclick="insertCommand('link ar1 es1 down')">Break Link</button>
            </div>
            <div style="font-size: 12px; opacity: 0.8; margin-bottom: 10px;">
                ✨ Try: help | status | h1 ping h5 | link ar1 es1 down | py net.controller.auto_detect_and_fix_failures()
            </div>
            <div class="command-output" id="command-output">
                <div class="log-entry log-info">🚀 Dashboard ready! Commands are sent to the main controller.
Type 'help' for available commands or 'status' to check connection.</div>
            </div>
        </div>
    </div>

    <script>
        let autoRefresh = null;
        let isExecuting = false;

        function addLogEntry(message, type = 'info') {
            const output = document.getElementById('command-output');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            output.appendChild(entry);
            output.scrollTop = output.scrollHeight;
            
            // Keep only last 50 entries
            while (output.children.length > 50) {
                output.removeChild(output.firstChild);
            }
        }

        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                const statusEl = document.getElementById('connection-status');
                
                if (data.connected) {
                    statusEl.className = 'status-indicator status-connected';
                    statusEl.textContent = '🟢 Controller Connected';
                    
                    // Update stats
                    const networkData = data.network_data;
                    if (networkData && networkData.links) {
                        const totalLinks = Object.keys(networkData.links).length;
                        const upLinks = Object.values(networkData.links).filter(status => status).length;
                        const totalNodes = data.total_nodes || '--';
                        
                        document.getElementById('total-nodes').textContent = totalNodes;
                        document.getElementById('total-links').textContent = totalLinks;
                        document.getElementById('link-health').textContent = networkData.health?.link_health + '%' || '--';
                        document.getElementById('connectivity').textContent = networkData.health?.connectivity_health + '%' || '--';
                        
                        // Update link status
                        updateLinkStatus(networkData.links);
                        
                        // Update topology
                        const topoResponse = await fetch('/api/topology');
                        const svgContent = await topoResponse.text();
                        document.getElementById('topology-svg').innerHTML = svgContent;
                    }
                } else {
                    statusEl.className = 'status-indicator status-disconnected';
                    statusEl.textContent = '🔴 Controller Disconnected';
                    document.getElementById('topology-svg').innerHTML = 
                        '<text x="500" y="300" text-anchor="middle" fill="white">Controller not connected</text>';
                }
            } catch (error) {
                console.error('Dashboard error:', error);
            }
        }

        function updateLinkStatus(links) {
            const container = document.getElementById('link-status');
            container.innerHTML = '';
            
            Object.entries(links).forEach(([linkName, status]) => {
                const item = document.createElement('div');
                item.className = 'link-item';
                item.innerHTML = `
                    <div class="link-dot ${status ? 'link-up' : 'link-down'}"></div>
                    <span>${linkName.replace('↔', '↔')}</span>
                `;
                container.appendChild(item);
            });
        }

        async function executeCommand() {
            if (isExecuting) {
                addLogEntry('⏳ Please wait for the current command to complete...', 'error');
                return;
            }
            
            const input = document.getElementById('command-input');
            const command = input.value.trim();
            const executeBtn = document.getElementById('execute-btn');
            
            if (!command) {
                addLogEntry('Please enter a command', 'error');
                return;
            }
            
            // Set executing state
            isExecuting = true;
            executeBtn.disabled = true;
            executeBtn.textContent = 'Executing...';
            
            addLogEntry(`> ${command}`, 'info');
            
            // Show loading for longer commands
            if (command.includes('ping') || command.includes('py net.controller')) {
                addLogEntry('⏳ Sending command to controller, please wait...', 'info');
            }
            
            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLogEntry(result.output || 'Command executed successfully', 'success');
                } else {
                    addLogEntry(result.error || 'Command failed', 'error');
                }
                
                input.value = '';
                
                // Refresh dashboard after certain commands
                if (command.includes('link') || command.includes('auto_detect') || command.includes('reset')) {
                    setTimeout(updateDashboard, 2000);
                }
                
            } catch (error) {
                addLogEntry(`Network error: ${error.message}`, 'error');
            } finally {
                // Reset executing state
                isExecuting = false;
                executeBtn.disabled = false;
                executeBtn.textContent = 'Execute';
            }
        }

        function insertCommand(cmd) {
            document.getElementById('command-input').value = cmd;
        }

        function handleEnter(event) {
            if (event.key === 'Enter' && !isExecuting) {
                executeCommand();
            }
        }




        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            addLogEntry('🌐 Dashboard initialized. Controller communication enabled.', 'info');
            updateDashboard();
            
            // Auto refresh every 10 seconds
            autoRefresh = setInterval(updateDashboard, 10000);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    connected, data = get_controller_data()
    
    if connected:
        network_data = data.get('data', {})
        
        # Count total nodes from links
        nodes = set()
        links = network_data.get('links', {})
        for link_name in links.keys():
            if '↔' in link_name:
                node1, node2 = link_name.split('↔')
                nodes.add(node1)
                nodes.add(node2)
        
        return jsonify({
            "connected": True,
            "message": f"Controller running (PID: {data.get('pid')})",
            "network_data": network_data,
            "total_nodes": len(nodes)
        })
    else:
        return jsonify({
            "connected": False,
            "message": "Controller not found or not responding"
        })

@app.route('/api/topology')
def api_topology():
    connected, data = get_controller_data()
    
    # Get nodes from links first
    if connected and 'data' in data:
        links = data['data'].get('links', {})
    else:
        links = {}
    
    nodes, connections = analyze_network_from_links(links)
    
    # Try to get additional nodes from controller (like hosts from connectivity tests)
    additional_nodes = get_all_network_nodes_from_controller()
    if additional_nodes:
        # Merge additional nodes with discovered nodes
        for layer, additional_list in additional_nodes.items():
            if layer in nodes:
                # Add any new nodes not already discovered
                for node in additional_list:
                    if node not in nodes[layer]:
                        nodes[layer].append(node)
                nodes[layer] = sorted(nodes[layer])
            else:
                nodes[layer] = sorted(additional_list)
    
    # Debug output
    print(f"🎨 Final topology nodes: {dict((k, len(v)) for k, v in nodes.items())}")
    
    # If we have no nodes at all, provide a message
    total_nodes = sum(len(v) for v in nodes.values())
    if total_nodes == 0:
        return '<text x="500" y="300" text-anchor="middle" fill="white" font-size="16">Network not initialized or no data available</text>'
    
    return generate_topology_svg(nodes, connections)

@app.route('/api/execute', methods=['POST'])
def api_execute():
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({"success": False, "error": "No command provided"})
        
        print(f"🌐 Dashboard API received command: {command}")
        success, output = execute_command(command)
        
        result = {
            "success": success,
            "output": output if success else None,
            "error": output if not success else None
        }
        
        print(f"🌐 Dashboard API returning: success={success}, output_length={len(output) if output else 0}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"API execution error: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({"success": False, "error": error_msg})

if __name__ == '__main__':
    print("🌐 WORKING Fat-Tree Dashboard - FULLY DYNAMIC")
    print("=" * 45)
    print("📋 Key Features:")
    print("   ✅ Controller communication via file exchange")
    print("   ✅ Proper command queuing and response handling")
    print("   ✅ 15-second timeout for controller responses")
    print("   ✅ Enhanced UI with loading states")
    print("   ✅ Help and status commands work locally")
    print("   ✅ All network commands sent to main controller")
    print("   ✅ FULLY DYNAMIC topology generation")
    print("   ✅ Automatic host detection and positioning")
    print("   ✅ Dynamic host-switch connection mapping")
    print()
    print("🚀 Starting on http://localhost:5000")
    print("📋 Make sure your main controller is running!")
    print("🔧 Commands will be sent to controller via /tmp/ files")
    print("🎯 Topology will show ALL nodes dynamically discovered")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
