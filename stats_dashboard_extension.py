#!/usr/bin/env python3
"""
stats_dashboard_extension.py
Dashboard extension for viewing network statistics
Admission control references removed
"""

from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime

# Enhanced HTML template with statistics
STATS_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Statistics Dashboard</title>
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
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stats-section {
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
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .latency-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            margin-bottom: 5px;
        }
        
        .latency-good { border-left: 4px solid #4CAF50; }
        .latency-ok { border-left: 4px solid #FF9800; }
        .latency-bad { border-left: 4px solid #F44336; }
        
        .chart-container {
            height: 200px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .control-buttons {
            text-align: center;
            margin: 20px 0;
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
        
        .btn.secondary { background: #2196F3; }
        .btn.warning { background: #FF9800; }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-active { background: #4CAF50; }
        .status-inactive { background: #F44336; }
        
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Network Statistics Dashboard</h1>
            <p>Real-time monitoring of Fat-Tree network performance</p>
            <div class="control-buttons">
                <button class="btn" onclick="toggleMonitoring()">Start Monitoring</button>
                <button class="btn secondary" onclick="refreshStats()">Refresh Stats</button>
                <button class="btn warning" onclick="downloadStats()">Download CSV</button>
            </div>
        </div>

        <div class="stats-grid">
            <!-- Traffic Statistics -->
            <div class="stats-section">
                <div class="section-title">📈 Traffic Statistics</div>
                <div id="traffic-stats">
                    <div class="metric-card">
                        <div class="metric-value" id="total-flows">--</div>
                        <div class="metric-label">Total Active Flows</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="total-packets">--</div>
                        <div class="metric-label">Total Packets</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="total-bytes">--</div>
                        <div class="metric-label">Total Bytes</div>
                    </div>
                </div>
            </div>

            <!-- Latency Statistics -->
            <div class="stats-section">
                <div class="section-title">⏱️ Latency Statistics</div>
                <div id="latency-stats">
                    <div class="metric-card">
                        <div class="metric-label">Loading latency data...</div>
                    </div>
                </div>
            </div>

            <!-- System Health -->
            <div class="stats-section">
                <div class="section-title">🔋 System Health</div>
                <div id="health-stats">
                    <div class="metric-card">
                        <div class="metric-value" id="link-health">--</div>
                        <div class="metric-label">Link Health</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="connectivity-health">--</div>
                        <div class="metric-label">Connectivity Health</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="monitoring-status">
                            <span class="status-indicator status-inactive"></span>
                            Stopped
                        </div>
                        <div class="metric-label">Monitoring Status</div>
                    </div>
                </div>
            </div>

            <!-- Network Statistics -->
            <div class="stats-section">
                <div class="section-title">📊 Network Statistics</div>
                <div id="network-stats">
                    <div class="metric-card">
                        <div class="metric-value" id="switch-count">--</div>
                        <div class="metric-label">Active Switches</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="host-count">--</div>
                        <div class="metric-label">Connected Hosts</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="utilization">--</div>
                        <div class="metric-label">Network Utilization</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Detailed Statistics Tables -->
        <div class="stats-section" style="grid-column: 1 / -1;">
            <div class="section-title">📋 Detailed Statistics</div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                <!-- Switch Statistics -->
                <div>
                    <h3 style="margin-bottom: 10px;">🔌 Switch Statistics</h3>
                    <div id="switch-stats" style="max-height: 300px; overflow-y: auto;">
                        <div style="opacity: 0.6;">No data available</div>
                    </div>
                </div>

                <!-- Host Pair Latencies -->
                <div>
                    <h3 style="margin-bottom: 10px;">🔗 Host Pair Latencies</h3>
                    <div id="host-latencies" style="max-height: 300px; overflow-y: auto;">
                        <div style="opacity: 0.6;">No data available</div>
                    </div>
                </div>
            </div>

            <!-- Mini Chart Placeholder -->
            <div class="chart-container">
                📈 Real-time charts coming soon...
                <br><small>Data is being collected in CSV files: ./network_stats/</small>
            </div>
        </div>
    </div>

    <script>
        let monitoringActive = false;
        let refreshInterval = null;
        let sessionStats = {
            startTime: new Date()
        };

        function toggleMonitoring() {
            const btn = event.target;
            
            if (!monitoringActive) {
                startMonitoring();
                btn.textContent = 'Stop Monitoring';
                btn.style.background = '#F44336';
                updateMonitoringStatus(true);
            } else {
                stopMonitoring();
                btn.textContent = 'Start Monitoring';
                btn.style.background = '#4CAF50';
                updateMonitoringStatus(false);
            }
        }

        function startMonitoring() {
            monitoringActive = true;
            refreshInterval = setInterval(refreshStats, 5000);
            refreshStats(); // Initial load
            console.log('📊 Statistics monitoring started');
        }

        function stopMonitoring() {
            monitoringActive = false;
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
            console.log('🛑 Statistics monitoring stopped');
        }

        function updateMonitoringStatus(active) {
            const statusElement = document.getElementById('monitoring-status');
            const indicator = statusElement.querySelector('.status-indicator');
            
            if (active) {
                indicator.className = 'status-indicator status-active';
                statusElement.innerHTML = '<span class="status-indicator status-active"></span>Active';
            } else {
                indicator.className = 'status-indicator status-inactive';
                statusElement.innerHTML = '<span class="status-indicator status-inactive"></span>Stopped';
            }
        }

        async function refreshStats() {
            try {
                // Get network status
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();
                
                updateNetworkStats(statusData);
                
                // Get statistics from files (if available)
                updateTrafficStats();
                updateLatencyStats();
                updateHealthStats(statusData);
                
            } catch (error) {
                console.error('Error refreshing stats:', error);
            }
        }

        function updateNetworkStats(data) {
            if (data.connected && data.network_data) {
                const networkData = data.network_data;
                
                // Count switches and hosts from links
                let switches = new Set();
                let hosts = new Set();
                
                if (networkData.links) {
                    Object.keys(networkData.links).forEach(link => {
                        if (link.includes('↔')) {
                            const [node1, node2] = link.split('↔');
                            if (node1.startsWith('es')) switches.add(node1);
                            if (node2.startsWith('es')) switches.add(node2);
                            if (node1.startsWith('h')) hosts.add(node1);
                            if (node2.startsWith('h')) hosts.add(node2);
                        }
                    });
                }
                
                document.getElementById('switch-count').textContent = switches.size;
                document.getElementById('host-count').textContent = hosts.size;
                
                // Calculate network utilization based on active links
                if (networkData.links) {
                    const totalLinks = Object.keys(networkData.links).length;
                    const upLinks = Object.values(networkData.links).filter(status => status).length;
                    const utilizationPercent = totalLinks > 0 ? ((upLinks / totalLinks) * 100).toFixed(1) : 0;
                    document.getElementById('utilization').textContent = utilizationPercent + '%';
                }
            }
        }

        function updateTrafficStats() {
            // Simulate traffic stats (would read from CSV files in real implementation)
            document.getElementById('total-flows').textContent = Math.floor(Math.random() * 20) + 5;
            document.getElementById('total-packets').textContent = (Math.floor(Math.random() * 50000) + 10000).toLocaleString();
            document.getElementById('total-bytes').textContent = (Math.floor(Math.random() * 5000000) + 1000000).toLocaleString();
        }

        function updateLatencyStats() {
            const latencyContainer = document.getElementById('latency-stats');
            
            // Simulate latency data (would read from CSV files in real implementation)
            const hostPairs = ['h1-h3', 'h1-h5', 'h1-h7', 'h3-h5', 'h3-h7', 'h5-h7'];
            let latencyHtml = '';
            
            hostPairs.forEach(pair => {
                const latency = (Math.random() * 20 + 1).toFixed(2);
                const latencyClass = latency < 5 ? 'latency-good' : latency < 15 ? 'latency-ok' : 'latency-bad';
                const status = latency < 5 ? '🟢' : latency < 15 ? '🟡' : '🔴';
                
                latencyHtml += `
                    <div class="latency-item ${latencyClass}">
                        <span>${status} ${pair}</span>
                        <span style="font-weight: bold">${latency} ms</span>
                    </div>
                `;
            });
            
            latencyContainer.innerHTML = latencyHtml;
            
            // Update detailed host latencies
            const hostLatenciesContainer = document.getElementById('host-latencies');
            hostLatenciesContainer.innerHTML = latencyHtml;
        }

        function updateHealthStats(data) {
            if (data.connected && data.network_data && data.network_data.health) {
                const health = data.network_data.health;
                
                document.getElementById('link-health').textContent = 
                    (health.link_health || 0) + '%';
                document.getElementById('connectivity-health').textContent = 
                    (health.connectivity_health || 0) + '%';
            }
        }

        function updateSwitchStats() {
            const switchContainer = document.getElementById('switch-stats');
            const switches = ['es1', 'es2', 'es3', 'es4'];
            
            let switchHtml = '';
            switches.forEach(switchName => {
                const flows = Math.floor(Math.random() * 10) + 1;
                const packets = Math.floor(Math.random() * 10000) + 1000;
                const bytes = Math.floor(Math.random() * 1000000) + 100000;
                
                switchHtml += `
                    <div class="metric-card" style="margin-bottom: 8px;">
                        <div style="font-weight: bold; margin-bottom: 5px;">🔌 ${switchName.toUpperCase()}</div>
                        <div style="font-size: 0.9em; opacity: 0.8;">
                            Flows: ${flows} | Packets: ${packets.toLocaleString()} | Bytes: ${bytes.toLocaleString()}
                        </div>
                    </div>
                `;
            });
            
            switchContainer.innerHTML = switchHtml;
        }

        function downloadStats() {
            // In a real implementation, this would download the CSV files
            alert('📁 Statistics CSV files are saved in: ./network_stats/\n\nFiles available:\n• traffic_stats.csv\n• latency_stats.csv\n• link_utilization.csv');
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            console.log('📊 Statistics dashboard initialized');
            updateSwitchStats();
            
            // Update switch stats periodically
            setInterval(updateSwitchStats, 10000);
        });
    </script>
</body>
</html>
'''

def create_stats_dashboard_app():
    """Create a Flask app for statistics dashboard"""
    app = Flask(__name__)
    
    @app.route('/stats')
    def stats_dashboard():
        return render_template_string(STATS_HTML_TEMPLATE)
    
    @app.route('/api/stats/traffic')
    def api_traffic_stats():
        """Get traffic statistics from CSV files"""
        try:
            stats_dir = './network_stats'
            traffic_file = f'{stats_dir}/traffic_stats.csv'
            
            if os.path.exists(traffic_file):
                # Read latest traffic stats from CSV
                with open(traffic_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # Skip header
                        latest_data = lines[-1].strip().split(',')
                        return jsonify({
                            'success': True,
                            'data': {
                                'timestamp': latest_data[0],
                                'switch': latest_data[1],
                                'total_packets': int(latest_data[2]),
                                'total_bytes': int(latest_data[3]),
                                'flow_count': int(latest_data[4])
                            }
                        })
            
            return jsonify({'success': False, 'error': 'No traffic data available'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/stats/latency')
    def api_latency_stats():
        """Get latency statistics from CSV files"""
        try:
            stats_dir = './network_stats'
            latency_file = f'{stats_dir}/latency_stats.csv'
            
            if os.path.exists(latency_file):
                # Read latest latency stats from CSV
                latencies = {}
                with open(latency_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        data = line.strip().split(',')
                        if len(data) >= 4:
                            pair = f"{data[1]}-{data[2]}"
                            latencies[pair] = float(data[3])
                
                return jsonify({
                    'success': True,
                    'data': latencies
                })
            
            return jsonify({'success': False, 'error': 'No latency data available'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return app

def add_stats_dashboard_to_existing_app(existing_app):
    """Add statistics routes to existing Flask app"""
    
    @existing_app.route('/stats')
    def stats_dashboard():
        return render_template_string(STATS_HTML_TEMPLATE)
    
    @existing_app.route('/api/stats/traffic')
    def api_traffic_stats():
        """Get traffic statistics from CSV files"""
        try:
            stats_dir = './network_stats'
            traffic_file = f'{stats_dir}/traffic_stats.csv'
            
            if os.path.exists(traffic_file):
                with open(traffic_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        latest_data = lines[-1].strip().split(',')
                        return jsonify({
                            'success': True,
                            'data': {
                                'timestamp': latest_data[0],
                                'switch': latest_data[1],
                                'total_packets': int(latest_data[2]),
                                'total_bytes': int(latest_data[3]),
                                'flow_count': int(latest_data[4])
                            }
                        })
            
            return jsonify({'success': False, 'error': 'No traffic data available'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    print("📊 Statistics dashboard added to existing app")
    print("🌐 Access at: http://localhost:5000/stats")

if __name__ == '__main__':
    # Standalone statistics dashboard
    app = create_stats_dashboard_app()
    print("📊 Starting Statistics Dashboard")
    print("🌐 Available at: http://localhost:5001/stats")
    app.run(host='0.0.0.0', port=5001, debug=True)
