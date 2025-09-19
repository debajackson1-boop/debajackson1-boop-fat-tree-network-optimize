#!/usr/bin/env python3
"""
dashboard_container_extension.py
Add container statistics to your existing dashboard WITHOUT modifying dashboard_core.py
"""

import os
import csv
import json
import subprocess
from flask import jsonify

def add_container_routes_to_dashboard(app):
    """
    Add container statistics routes to your existing Flask dashboard app
    Call this function in dashboard_core.py after creating the Flask app
    """
    
    @app.route('/api/stats/containers')
    def api_container_stats():
        """Get container statistics"""
        try:
            container_file = './network_stats/container_stats.csv'
            
            if os.path.exists(container_file):
                # Read latest container stats
                with open(container_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # Skip header
                        # Get latest entries for each container
                        h1_stats = None
                        h3_stats = None
                        
                        # Read from end to get latest
                        for line in reversed(lines[1:]):
                            data = line.strip().split(',')
                            if len(data) >= 8:
                                host = data[1]
                                if host == 'h1' and h1_stats is None:
                                    h1_stats = {
                                        'timestamp': data[0],
                                        'host': data[1],
                                        'container': data[2],
                                        'status': data[3],
                                        'cpu_percent': float(data[4]) if data[4] != '0' else 0,
                                        'memory_mb': float(data[5]) if data[5] != '0' else 0,
                                        'network_rx_mb': float(data[6]) if data[6] != '0' else 0,
                                        'network_tx_mb': float(data[7]) if data[7] != '0' else 0
                                    }
                                elif host == 'h3' and h3_stats is None:
                                    h3_stats = {
                                        'timestamp': data[0],
                                        'host': data[1],
                                        'container': data[2],
                                        'status': data[3],
                                        'cpu_percent': float(data[4]) if data[4] != '0' else 0,
                                        'memory_mb': float(data[5]) if data[5] != '0' else 0,
                                        'network_rx_mb': float(data[6]) if data[6] != '0' else 0,
                                        'network_tx_mb': float(data[7]) if data[7] != '0' else 0
                                    }
                        
                        container_data = {}
                        if h1_stats:
                            container_data['h1'] = h1_stats
                        if h3_stats:
                            container_data['h3'] = h3_stats
                        
                        return jsonify({'success': True, 'data': container_data})
            
            return jsonify({'success': False, 'error': 'No container data available'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/stats/container_summary')
    def api_container_summary():
        """Get container summary statistics"""
        try:
            history_file = './network_logs/container_history.csv'
            
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # Skip header
                        latest = lines[-1].strip().split(',')
                        if len(latest) >= 11:
                            return jsonify({
                                'success': True,
                                'data': {
                                    'timestamp': latest[0],
                                    'total_containers': int(latest[1]),
                                    'running_containers': int(latest[2]),
                                    'avg_cpu_percent': float(latest[3]),
                                    'total_memory_mb': float(latest[4]),
                                    'h1_status': latest[5],
                                    'h3_status': latest[6],
                                    'h1_cpu': float(latest[7]) if latest[7] != '0' else 0,
                                    'h3_cpu': float(latest[8]) if latest[8] != '0' else 0,
                                    'h1_memory': float(latest[9]) if latest[9] != '0' else 0,
                                    'h3_memory': float(latest[10]) if latest[10] != '0' else 0
                                }
                            })
            
            return jsonify({'success': False, 'error': 'No container summary available'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    print("🐳 Container statistics routes added to dashboard")
    print("📊 Available at: /api/stats/containers and /api/stats/container_summary")

def get_container_dashboard_html():
    """
    Return HTML/JavaScript code to add to your dashboard template
    This adds a container statistics section
    """
    
    html_section = '''
<!-- Container Statistics Section - ADD THIS TO YOUR DASHBOARD HTML -->
<div class="dashboard-section">
    <div class="section-title">🐳 Container Statistics</div>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="running-containers">--</div>
            <div>Running Containers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="avg-container-cpu">--</div>
            <div>Avg CPU Usage</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="total-container-memory">--</div>
            <div>Total Memory</div>
        </div>
    </div>
    
    <!-- Individual Container Stats -->
    <div class="section-title" style="margin-top: 15px;">📊 Individual Containers</div>
    <div class="stats-grid" id="container-stats">
        Loading container data...
    </div>
</div>
'''

    javascript_section = '''
// Container Statistics JavaScript - ADD THIS TO YOUR DASHBOARD SCRIPT SECTION

async function updateContainerStats() {
    try {
        // Get individual container stats
        const containerResponse = await fetch('/api/stats/containers');
        const containerData = await containerResponse.json();
        
        if (containerData.success && containerData.data) {
            updateContainerDisplay(containerData.data);
        }
        
        // Get container summary
        const summaryResponse = await fetch('/api/stats/container_summary');
        const summaryData = await summaryResponse.json();
        
        if (summaryData.success && summaryData.data) {
            updateContainerSummary(summaryData.data);
        }
        
    } catch (error) {
        console.error('Error updating container stats:', error);
    }
}

function updateContainerDisplay(containers) {
    let containerHtml = '';
    
    Object.entries(containers).forEach(([host, stats]) => {
        const statusColor = stats.status === 'running' ? '#4CAF50' : '#F44336';
        const statusIcon = stats.status === 'running' ? '🟢' : '🔴';
        
        containerHtml += `
            <div class="stat-card" style="border-left: 4px solid ${statusColor};">
                <div style="font-weight: bold; margin-bottom: 5px;">
                    ${statusIcon} ${host.toUpperCase()} Container
                </div>
                <div style="font-size: 0.9em; opacity: 0.8;">
                    Status: ${stats.status}<br>
                    CPU: ${stats.cpu_percent.toFixed(1)}%<br>
                    Memory: ${stats.memory_mb.toFixed(1)} MB<br>
                    Container: ${stats.container}
                </div>
            </div>
        `;
    });
    
    const containerSection = document.getElementById('container-stats');
    if (containerSection) {
        containerSection.innerHTML = containerHtml;
    }
}

function updateContainerSummary(summary) {
    const runningElement = document.getElementById('running-containers');
    const cpuElement = document.getElementById('avg-container-cpu');
    const memoryElement = document.getElementById('total-container-memory');
    
    if (runningElement) {
        runningElement.textContent = `${summary.running_containers}/${summary.total_containers}`;
    }
    if (cpuElement) {
        cpuElement.textContent = summary.avg_cpu_percent.toFixed(1) + '%';
    }
    if (memoryElement) {
        memoryElement.textContent = summary.total_memory_mb.toFixed(1) + ' MB';
    }
}

// ADD THIS LINE TO YOUR EXISTING updateDashboard() FUNCTION:
// updateContainerStats();
'''

    return html_section, javascript_section

# INTEGRATION INSTRUCTIONS FOR YOUR EXISTING DASHBOARD
integration_instructions = """
🔧 SAFE Integration Instructions for Your Dashboard:

1. In your dashboard_core.py, after creating the Flask app, add this line:
   from dashboard_container_extension import add_container_routes_to_dashboard
   add_container_routes_to_dashboard(app)

2. Add the container HTML section to your dashboard template (see get_container_dashboard_html())

3. Add the container JavaScript to your dashboard script section

4. In your existing updateDashboard() function, add this line:
   updateContainerStats();

That's it! Your dashboard will now show container statistics automatically.
"""

if __name__ == '__main__':
    print("🐳 Container Dashboard Extension")
    print("=" * 35)
    print(integration_instructions)
    
    # Show the HTML and JavaScript code
    html, js = get_container_dashboard_html()
    
    print("\n📋 HTML Section to Add:")
    print(html)
    
    print("\n📋 JavaScript Section to Add:")
    print(js)
