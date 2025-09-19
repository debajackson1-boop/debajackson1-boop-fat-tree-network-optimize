#!/usr/bin/env python3
"""
dashboard_container_api.py
Add container stats to your dashboard - ADD THESE ROUTES TO YOUR DASHBOARD
"""

import os
import csv
import json
from flask import jsonify

# ADD THESE ROUTES TO YOUR dashboard_core.py or working_dashboard.py

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

# ADD THIS JAVASCRIPT TO YOUR DASHBOARD HTML TEMPLATE:

CONTAINER_DASHBOARD_JS = '''
// Add this to your dashboard HTML template in the <script> section

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
    // Update container section (add this HTML section to your dashboard)
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
    
    // Update the container stats section (you'll need to add this div to your HTML)
    const containerSection = document.getElementById('container-stats');
    if (containerSection) {
        containerSection.innerHTML = containerHtml;
    }
}

function updateContainerSummary(summary) {
    // Update summary metrics
    document.getElementById('running-containers').textContent = 
        `${summary.running_containers}/${summary.total_containers}`;
    document.getElementById('avg-container-cpu').textContent = 
        summary.avg_cpu_percent.toFixed(1) + '%';
    document.getElementById('total-container-memory').textContent = 
        summary.total_memory_mb.toFixed(1) + ' MB';
}

// Add container stats to your existing updateDashboard() function:
// Call updateContainerStats() in your main update loop
'''

# HTML SECTION TO ADD TO YOUR DASHBOARD:

CONTAINER_DASHBOARD_HTML = '''
<!-- Add this section to your dashboard HTML -->

<!-- Container Statistics Section -->
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

print("📋 Dashboard Integration Instructions:")
print("=" * 40)
print("1. Add the two API routes (@app.route) to your dashboard file")
print("2. Add the HTML section to your dashboard template")
print("3. Add the JavaScript to your dashboard script section")
print("4. Call updateContainerStats() in your main dashboard update loop")
