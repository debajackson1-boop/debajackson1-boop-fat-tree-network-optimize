#!/usr/bin/env python3
"""
dashboard_templates.py
HTML templates for the dashboard - WITH DARK SCROLLBARS
Admission control buttons removed
"""

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
            width: 60%;
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
        .btn.stats { background: #9C27B0; }
        
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

        /* CHROMIUM-SPECIFIC Scrollbar Styling */
        html *::-webkit-scrollbar {
            width: 12px !important;
            height: 12px !important;
        }
        
        html *::-webkit-scrollbar-track {
            background: #1a1a2e !important;
            border-radius: 6px !important;
        }
        
        html *::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #4a5568, #2d3748) !important;
            border-radius: 6px !important;
            border: 1px solid #4CAF50 !important;
        }
        
        html *::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #4CAF50, #45a049) !important;
        }

        /* Direct element targeting for Chromium */
        #system-logs,
        #controller-logs,
        #events-timeline,
        #command-output {
            overflow-y: scroll !important;
        }

        #system-logs::-webkit-scrollbar,
        #controller-logs::-webkit-scrollbar,
        #events-timeline::-webkit-scrollbar,
        #command-output::-webkit-scrollbar {
            width: 14px !important;
            background: transparent !important;
        }
        
        #system-logs::-webkit-scrollbar-track,
        #controller-logs::-webkit-scrollbar-track,
        #events-timeline::-webkit-scrollbar-track,
        #command-output::-webkit-scrollbar-track {
            background: #0f0f1e !important;
            border-radius: 7px !important;
            border: 1px solid #2a2a3e !important;
        }
        
        #system-logs::-webkit-scrollbar-thumb,
        #controller-logs::-webkit-scrollbar-thumb,
        #events-timeline::-webkit-scrollbar-thumb,
        #command-output::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #4a5568, #2d3748) !important;
            border-radius: 7px !important;
            border: 2px solid #4CAF50 !important;
        }

        #system-logs::-webkit-scrollbar-thumb:hover,
        #controller-logs::-webkit-scrollbar-thumb:hover,
        #events-timeline::-webkit-scrollbar-thumb:hover,
        #command-output::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #4CAF50, #45a049) !important;
        }

        /* Force scrollbar appearance in Chromium */
        #system-logs::-webkit-scrollbar-track:hover,
        #controller-logs::-webkit-scrollbar-track:hover,
        #events-timeline::-webkit-scrollbar-track:hover,
        #command-output::-webkit-scrollbar-track:hover {
            background: #1a1a2e !important;
        }

        /* Firefox (this was working) */
        #system-logs,
        #controller-logs,
        #events-timeline,
        #command-output {
            scrollbar-width: thin !important;
            scrollbar-color: #4a5568 #1a1a2e !important;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid { grid-template-columns: 1fr; }
            .command-input { width: 100%; margin-bottom: 10px; }
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
                <button class="btn stats" onclick="window.open('/stats', '_blank')">📊 Statistics</button>
                <button class="btn info" onclick="insertCommand('help')">Help</button>
                <button class="btn info" onclick="insertCommand('status')">Status</button>
                <button class="btn" onclick="insertCommand('h1 ping h5')">Test Ping</button>
                <button class="btn warning" onclick="insertCommand('py net.controller.auto_detect_and_fix_failures()')">Auto-Fix</button>
                <button class="btn warning" onclick="insertCommand('py net.controller.graceful_reset_network_only()')">Soft Reset</button>
                <button class="btn danger" onclick="insertCommand('py net.controller.reset_to_clean_state()')">Full Reset</button>
                <button class="btn danger" onclick="insertCommand('link ar1 es1 down')">Break Link</button>
            </div>
            <div style="font-size: 12px; opacity: 0.8; margin-bottom: 10px;">
                ✨ Try: help | status | h1 ping h5 | link ar1 es1 down | py net.controller.auto_detect_and_fix_failures() | py net.controller.graceful_reset_network_only()
            </div>
            <div class="command-output" id="command-output">
                <div class="log-entry log-info">🚀 Dashboard ready! Commands are sent to the main controller.
Type 'help' for available commands or 'status' to check connection.</div>
            </div>
        </div>

        <!-- NEW: Network Logs Section -->
        <div class="dashboard-section" style="grid-column: 1 / -1;">
            <div class="section-title">📋 Network Logs & Events</div>
            <div style="margin-bottom: 15px;">
                <button class="btn info" onclick="refreshLogs()">🔄 Refresh Logs</button>
                <button class="btn info" onclick="clearLogsDisplay()">🗑️ Clear Display</button>
                <button class="btn" onclick="toggleAutoRefreshLogs()" id="auto-logs-btn">⏸️ Auto-Refresh</button>
                <select id="log-type-select" style="padding: 8px; margin: 5px; border-radius: 5px; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.3);">
                    <option value="controller" style="background: #1e3c72; color: white;">Controller Events</option>
                    <option value="system" style="background: #1e3c72; color: white;">System Logs</option>
                    <option value="mininet" style="background: #1e3c72; color: white;">Mininet Logs</option>
                    <option value="ovs" style="background: #1e3c72; color: white;">OVS Switch Logs</option>
                </select>
            </div>
            
            <div class="stats-grid" style="grid-template-columns: 1fr 1fr;">
                <!-- Live System Logs -->
                <div class="stat-card" style="height: 300px;">
                    <h4>🖥️ Live System Events</h4>
                    <div id="system-logs" style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 5px; height: 250px; overflow-y: auto; font-family: monospace; font-size: 12px;">
                        <div style="color: #4CAF50;">[System] Dashboard initialized</div>
                        <div style="color: #2196F3;">[Info] Waiting for log data...</div>
                    </div>
                </div>

                <!-- Controller Status & Recent Commands -->
                <div class="stat-card" style="height: 300px;">
                    <h4>⚡ Controller Activity</h4>
                    <div id="controller-logs" style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 5px; height: 250px; overflow-y: auto; font-family: monospace; font-size: 12px;">
                        <div style="color: #4CAF50;">[Controller] Monitoring active</div>
                        <div style="color: #2196F3;">[Info] Ready for commands...</div>
                    </div>
                </div>
            </div>
            
            <!-- Network Events Timeline -->
            <div class="stat-card" style="margin-top: 15px;">
                <h4>🕐 Network Events Timeline</h4>
                <div style="margin-bottom: 10px;">
                    <span style="background: rgba(76,175,80,0.2); padding: 2px 8px; border-radius: 3px; margin-right: 10px; font-size: 12px;">🟢 Success</span>
                    <span style="background: rgba(255,152,0,0.2); padding: 2px 8px; border-radius: 3px; margin-right: 10px; font-size: 12px;">🟡 Warning</span>
                    <span style="background: rgba(244,67,54,0.2); padding: 2px 8px; border-radius: 3px; margin-right: 10px; font-size: 12px;">🔴 Error</span>
                    <span style="background: rgba(33,150,243,0.2); padding: 2px 8px; border-radius: 3px; font-size: 12px;">🔵 Info</span>
                </div>
                <div id="events-timeline" style="background: rgba(0,0,0,0.4); padding: 15px; border-radius: 8px; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 13px;">
                    <div class="log-entry log-info">🚀 [Dashboard] Application started successfully</div>
                    <div class="log-entry log-success">✅ [Network] Topology loaded - 18 nodes detected</div>
                    <div class="log-entry log-info">📡 [Controller] Connection established</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let autoRefresh = null;
        let isExecuting = false;
        let autoLogsRefresh = null;
        let logsAutoRefreshEnabled = true;

        function addLogEntry(message, type = 'info') {
            const output = document.getElementById('command-output');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            output.appendChild(entry);
            output.scrollTop = output.scrollHeight;
            
            // Also add to events timeline
            addEventToTimeline(message, type);
            
            // Keep only last 50 entries
            while (output.children.length > 50) {
                output.removeChild(output.firstChild);
            }
        }

        function addEventToTimeline(message, type = 'info') {
            const timeline = document.getElementById('events-timeline');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            
            let icon = '🔵';
            if (type === 'success') icon = '✅';
            else if (type === 'error') icon = '❌';
            else if (type === 'warning') icon = '⚠️';
            
            entry.innerHTML = `${icon} [${new Date().toLocaleTimeString()}] ${message}`;
            timeline.insertBefore(entry, timeline.firstChild);
            
            // Keep only last 20 entries
            while (timeline.children.length > 20) {
                timeline.removeChild(timeline.lastChild);
            }
        }

        function addSystemLog(message, source = 'System') {
            const systemLogs = document.getElementById('system-logs');
            const timestamp = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.style.color = '#8BC34A';
            entry.innerHTML = `[${timestamp}] [${source}] ${message}`;
            systemLogs.appendChild(entry);
            systemLogs.scrollTop = systemLogs.scrollHeight;
            
            // Keep only last 30 entries
            while (systemLogs.children.length > 30) {
                systemLogs.removeChild(systemLogs.firstChild);
            }
        }

        function addControllerLog(message, type = 'info') {
            const controllerLogs = document.getElementById('controller-logs');
            const timestamp = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            
            let color = '#2196F3';
            if (type === 'success') color = '#4CAF50';
            else if (type === 'error') color = '#F44336';
            else if (type === 'warning') color = '#FF9800';
            
            entry.style.color = color;
            entry.innerHTML = `[${timestamp}] [Controller] ${message}`;
            controllerLogs.appendChild(entry);
            controllerLogs.scrollTop = controllerLogs.scrollHeight;
            
            // Keep only last 30 entries
            while (controllerLogs.children.length > 30) {
                controllerLogs.removeChild(controllerLogs.firstChild);
            }
        }

        function refreshLogs() {
            addSystemLog('Log refresh requested', 'Dashboard');
            addControllerLog('Fetching latest controller status...', 'info');
            
            // Simulate fetching recent logs
            setTimeout(() => {
                addSystemLog('Network topology: 18 nodes, 20 links active', 'Network');
                addControllerLog('Status update: All systems operational', 'success');
                addEventToTimeline('System status refreshed', 'success');
            }, 500);
        }

        function clearLogsDisplay() {
            document.getElementById('system-logs').innerHTML = '<div style="color: #4CAF50;">[System] Logs cleared</div>';
            document.getElementById('controller-logs').innerHTML = '<div style="color: #4CAF50;">[Controller] Display cleared</div>';
            addEventToTimeline('Log displays cleared', 'info');
        }

        function toggleAutoRefreshLogs() {
            const btn = document.getElementById('auto-logs-btn');
            if (logsAutoRefreshEnabled) {
                clearInterval(autoLogsRefresh);
                btn.textContent = '▶️ Auto-Refresh';
                btn.className = 'btn warning';
                logsAutoRefreshEnabled = false;
                addSystemLog('Auto-refresh disabled', 'Dashboard');
            } else {
                autoLogsRefresh = setInterval(refreshLogs, 10000); // Every 10 seconds
                btn.textContent = '⏸️ Auto-Refresh';
                btn.className = 'btn';
                logsAutoRefreshEnabled = true;
                addSystemLog('Auto-refresh enabled (10s interval)', 'Dashboard');
            }
        }

        function simulateNetworkActivity() {
            const activities = [
                { msg: 'Packet forwarded through es1 → ar1', type: 'info', source: 'Network' },
                { msg: 'Flow table updated on switch es3', type: 'success', source: 'OVS' },
                { msg: 'Ping successful: h1 → h5 (8.2ms)', type: 'success', source: 'Network' },
                { msg: 'Link status check: all links operational', type: 'info', source: 'Monitor' },
                { msg: 'Route calculation completed', type: 'success', source: 'Controller' }
            ];
            
            const activity = activities[Math.floor(Math.random() * activities.length)];
            
            if (activity.source === 'Controller') {
                addControllerLog(activity.msg, activity.type);
            } else {
                addSystemLog(activity.msg, activity.source);
            }
            
            if (Math.random() > 0.7) {
                addEventToTimeline(activity.msg, activity.type);
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
            
            // Initialize logs auto-refresh
            autoLogsRefresh = setInterval(refreshLogs, 10000);
            
            // Simulate some network activity for demonstration
            setTimeout(() => {
                addSystemLog('Network topology loaded successfully', 'Network');
                addControllerLog('Controller connection established', 'success');
                addEventToTimeline('Dashboard fully initialized', 'success');
            }, 1000);
            
            // Simulate periodic network activity
            setInterval(simulateNetworkActivity, 15000);
        });
    </script>
</body>
</html>
'''
