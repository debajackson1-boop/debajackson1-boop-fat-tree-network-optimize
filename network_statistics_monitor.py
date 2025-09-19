#!/usr/bin/env python3
"""
network_statistics_monitor.py
Independent statistics collection for Fat-Tree network
UPDATED: REAL PING MEASUREMENTS + HISTORY LOGGING + MONITORING TOGGLE
"""

import time
import json
import threading
import subprocess
import os
import re
import csv
import requests  # For dashboard communication
from datetime import datetime
from collections import defaultdict, deque
from container_stats_addon import ContainerStatsAddon

# NEW: Import monitoring toggle
from monitoring_toggle import print_stats, print_important, print_error

class NetworkStatsMonitor:
    """Independent network statistics monitor with real ping measurements and history logging"""
    
    def __init__(self, monitor_interval=5):
        self.monitor_interval = monitor_interval
        self.running = False
        self.stats_thread = None
        

        # Data storage
        self.traffic_stats = defaultdict(lambda: deque(maxlen=100))
        self.latency_stats = defaultdict(lambda: deque(maxlen=100))
        self.admission_stats = deque(maxlen=200)
        self.link_utilization = defaultdict(lambda: deque(maxlen=100))
        
        # Output directories
        self.stats_dir = './network_stats'
        self.logs_dir = './network_logs'  # ADDED: History logs directory
        self.ensure_directories()
        self.container_addon = ContainerStatsAddon(self.stats_dir)
        # History log files
        self.traffic_history = os.path.join(self.logs_dir, 'traffic_history.csv')
        self.latency_history = os.path.join(self.logs_dir, 'latency_history.csv')
        self.health_history = os.path.join(self.logs_dir, 'health_history.csv')
        self.events_log = os.path.join(self.logs_dir, 'events.log')
        self.daily_summary = os.path.join(self.logs_dir, f'daily_summary_{datetime.now().strftime("%Y%m%d")}.json')
        
        # Initialize history log files
        self._initialize_history_logs()
        
        # Network topology (Fat-Tree specific)
        self.hosts = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8']
        self.switches = ['es1', 'es2', 'es3', 'es4']
        self.routers = ['ar1', 'ar2', 'ar3', 'ar4', 'cr1', 'cr2']
        
        # Test pairs for latency monitoring
        self.latency_test_pairs = [
            ('h1', 'h3'), ('h1', 'h5'), ('h1', 'h7'),
            ('h3', 'h5'), ('h3', 'h7'), ('h5', 'h7'),
            ('h2', 'h4'), ('h2', 'h6'), ('h2', 'h8')
        ]
        
        print_important("📊 Network Statistics Monitor initialized")
        print_important(f"📁 Stats directory: {self.stats_dir}")
        print_important(f"📚 History logs directory: {self.logs_dir}")
        print_important("🎯 REAL PING MEASUREMENTS + HISTORY LOGGING")
        
        # Log initialization
        self._log_event("Network Statistics Monitor initialized", "INFO")
    
    def ensure_directories(self):
        """Create stats and logs directories if they don't exist"""
        for directory in [self.stats_dir, self.logs_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print_important(f"📁 Created directory: {directory}")
    
    def _initialize_history_logs(self):
        """Initialize history log CSV files with headers if they don't exist"""
        
        # Traffic history headers
        if not os.path.exists(self.traffic_history):
            with open(self.traffic_history, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'total_packets', 'total_bytes', 'total_flows', 
                               'avg_packet_size', 'busiest_switch', 'es1_packets', 'es2_packets', 
                               'es3_packets', 'es4_packets'])
        
        # Latency history headers
        if not os.path.exists(self.latency_history):
            with open(self.latency_history, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'avg_latency', 'min_latency', 'max_latency', 
                               'pair_count', 'h1_h3', 'h1_h5', 'h1_h7', 'h3_h5', 'h3_h7', 
                               'h5_h7', 'h2_h6', 'h4_h8'])
        
        # Health history headers
        if not os.path.exists(self.health_history):
            with open(self.health_history, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'link_health', 'connectivity_health', 
                               'total_links', 'links_up', 'overall_status'])
    
    def _log_event(self, message, level="INFO"):
        """Log events to text file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            with open(self.events_log, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            print_error(f"❌ Error logging event: {e}")
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.running:
            print_important("⚠️ Monitor already running")
            return
        
        self.running = True
        self.stats_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.stats_thread.start()
        
        print_important("🚀 Network monitoring started")
        print_important(f"📊 Collecting stats every {self.monitor_interval} seconds")
        print_important("📁 Current stats files:")
        print_important(f"   • {self.stats_dir}/traffic_stats.csv")
        print_important(f"   • {self.stats_dir}/latency_stats.csv")
        print_important(f"   • {self.stats_dir}/admission_stats.csv")
        print_important(f"   • {self.stats_dir}/link_utilization.csv")
        print_important("📚 History log files:")
        print_important(f"   • {self.traffic_history}")
        print_important(f"   • {self.latency_history}")
        print_important(f"   • {self.health_history}")
        print_important(f"   • {self.events_log}")
        print_stats("🎯 Latency: REAL ping measurements only via dashboard")
        
        self._log_event("Network monitoring started", "INFO")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.stats_thread:
            self.stats_thread.join(timeout=5)
        print_important("🛑 Network monitoring stopped")
        self._log_event("Network monitoring stopped", "INFO")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                timestamp = datetime.now()
                
                # Collect different types of statistics
                traffic_data = self._collect_traffic_stats(timestamp)
                latency_data = self._collect_latency_stats(timestamp)
                health_data = self._collect_admission_stats(timestamp)
                self._collect_link_stats(timestamp)
                
                # Save to current stats files
                self._save_stats_to_files()
                self.container_addon.collect_container_stats()
                # ADDED: Save to history logs
                if traffic_data:
                    self._log_traffic_history(traffic_data)
                if latency_data:
                    self._log_latency_history(latency_data)
                if health_data:
                    self._log_health_history(health_data)
                
                time.sleep(self.monitor_interval)
                

            except Exception as e:
                print_error(f"⚠️ Monitoring error: {e}")
                self._log_event(f"Monitoring error: {e}", "ERROR")
                time.sleep(self.monitor_interval)
    
    def _collect_traffic_stats(self, timestamp):
        """Collect traffic statistics from switches"""
        try:
            traffic_data = {}
            for switch in self.switches:
                stats = self._get_switch_traffic_stats(switch)
                if stats:
                    stats['timestamp'] = timestamp
                    self.traffic_stats[switch].append(stats)
                    traffic_data[switch] = stats
            return traffic_data
        except Exception as e:
            print_error(f"⚠️ Error collecting traffic stats: {e}")
            return None
    
    def _get_switch_traffic_stats(self, switch):
        """Get traffic statistics for a specific switch"""
        try:
            # Get flow statistics from OpenFlow
            cmd = f"ovs-ofctl dump-flows {switch}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            total_packets = 0
            total_bytes = 0
            flow_count = 0
            
            for line in result.stdout.split('\n'):
                if 'n_packets=' in line and 'n_bytes=' in line:
                    flow_count += 1
                    
                    # Extract packet count
                    packet_match = re.search(r'n_packets=(\d+)', line)
                    if packet_match:
                        total_packets += int(packet_match.group(1))
                    
                    # Extract byte count
                    byte_match = re.search(r'n_bytes=(\d+)', line)
                    if byte_match:
                        total_bytes += int(byte_match.group(1))
            
            return {
                'switch': switch,
                'total_packets': total_packets,
                'total_bytes': total_bytes,
                'flow_count': flow_count,
                'avg_packet_size': total_bytes / total_packets if total_packets > 0 else 0
            }
            
        except Exception as e:
            print_error(f"⚠️ Error getting stats for {switch}: {e}")
            return None
    
    def _collect_latency_stats(self, timestamp):
        """REAL PING MEASUREMENTS ONLY with history logging"""
        try:
            real_measurements = 0
            latency_data = {}
            print_stats("📊 Collecting REAL latency measurements only...")
            
            for src, dst in self.latency_test_pairs:
                try:
                    # Execute real ping via dashboard
                    ping_command = f"{src} ping -c 1 -W 2 {dst}"
                    response = requests.post('http://localhost:5000/api/execute', 
                                           json={'command': ping_command}, 
                                           timeout=8)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            output = result.get('output', '')
                            if 'time=' in output:
                                # Parse latency from ping output
                                time_match = re.search(r'time=([\d.]+)', output)
                                if time_match:
                                    latency = float(time_match.group(1))
                                    
                                    # Store the measurement
                                    self.latency_stats[f"{src}-{dst}"].append({
                                        'timestamp': timestamp,
                                        'src': src,
                                        'dst': dst,
                                        'latency_ms': latency,
                                        'status': 'real_ping'
                                    })
                                    
                                    # Store for history logging
                                    latency_data[f"{src}-{dst}"] = latency
                                    real_measurements += 1
                                    print_stats(f"📊 REAL {src}→{dst}: {latency:.3f}ms")
                    
                    # Small delay between pings
                    time.sleep(0.2)
                    
                except Exception as e:
                    print_stats(f"❌ {src}→{dst}: ping error - {e}")
                    continue
            
            if real_measurements > 0:
                print_stats(f"✅ Collected {real_measurements}/{len(self.latency_test_pairs)} REAL latency measurements")
                self._log_event(f"Collected {real_measurements} real latency measurements", "INFO")
            else:
                print_stats("⚠️ No real latency measurements available this cycle")
                self._log_event("No real latency measurements available", "WARNING")
            
            return latency_data if real_measurements > 0 else None
                
        except Exception as e:
            print_error(f"❌ Error in real latency collection: {e}")
            self._log_event(f"Latency collection error: {e}", "ERROR")
            return None
    
    def _collect_admission_stats(self, timestamp):
        """Collect admission control statistics"""
        try:
            # Read admission control status from controller status file
            status_file = '/tmp/fat_tree_status.json'
            
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    controller_data = json.load(f)
                
                if 'data' in controller_data:
                    network_data = controller_data['data']
                    
                    # Extract admission control relevant data
                    admission_info = {
                        'timestamp': timestamp,
                        'total_links': len(network_data.get('links', {})),
                        'links_up': sum(1 for status in network_data.get('links', {}).values() if status),
                        'link_health': network_data.get('health', {}).get('link_health', 0),
                        'connectivity_health': network_data.get('health', {}).get('connectivity_health', 0),
                        'overall_status': network_data.get('health', {}).get('overall_status', 'Unknown')
                    }
                    
                    self.admission_stats.append(admission_info)
                    return admission_info
            return None
        
        except Exception as e:
            print_error(f"⚠️ Error collecting admission stats: {e}")
            return None
    
    def _collect_link_stats(self, timestamp):
        """Collect link utilization statistics"""
        try:
            # Read link utilization from controller if available
            status_file = '/tmp/fat_tree_status.json'
            
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    controller_data = json.load(f)
                
                if 'data' in controller_data and 'links' in controller_data['data']:
                    links = controller_data['data']['links']
                    
                    for link_name, status in links.items():
                        link_stat = {
                            'timestamp': timestamp,
                            'link': link_name,
                            'status': 'up' if status else 'down',
                            'utilization': 0
                        }
                        
                        self.link_utilization[link_name].append(link_stat)
        
        except Exception as e:
            print_error(f"⚠️ Error collecting link stats: {e}")
    
    def _log_traffic_history(self, traffic_data):
        """Log traffic statistics to history file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate totals
            total_packets = sum(switch.get('total_packets', 0) for switch in traffic_data.values())
            total_bytes = sum(switch.get('total_bytes', 0) for switch in traffic_data.values())
            total_flows = sum(switch.get('flow_count', 0) for switch in traffic_data.values())
            avg_packet_size = total_bytes / total_packets if total_packets > 0 else 0
            
            # Find busiest switch
            busiest_switch = max(traffic_data.items(), 
                               key=lambda x: x[1].get('total_packets', 0))[0] if traffic_data else 'none'
            
            # Individual switch data
            switch_packets = {f'{switch}_packets': data.get('total_packets', 0) 
                            for switch, data in traffic_data.items()}
            
            with open(self.traffic_history, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, total_packets, total_bytes, total_flows, 
                    avg_packet_size, busiest_switch,
                    switch_packets.get('es1_packets', 0),
                    switch_packets.get('es2_packets', 0),
                    switch_packets.get('es3_packets', 0),
                    switch_packets.get('es4_packets', 0)
                ])
            
            print_stats(f"📚 Traffic history logged: {total_packets} packets, busiest: {busiest_switch}")
            
        except Exception as e:
            print_error(f"❌ Error logging traffic history: {e}")
    
    def _log_latency_history(self, latency_data):
        """Log latency statistics to history file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if latency_data:
                latencies = [v for v in latency_data.values() if v > 0]
                avg_latency = sum(latencies) / len(latencies) if latencies else 0
                min_latency = min(latencies) if latencies else 0
                max_latency = max(latencies) if latencies else 0
                pair_count = len(latencies)
                
                with open(self.latency_history, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp, avg_latency, min_latency, max_latency, pair_count,
                        latency_data.get('h1-h3', 0),
                        latency_data.get('h1-h5', 0),
                        latency_data.get('h1-h7', 0),
                        latency_data.get('h3-h5', 0),
                        latency_data.get('h3-h7', 0),
                        latency_data.get('h5-h7', 0),
                        latency_data.get('h2-h6', 0),
                        latency_data.get('h4-h8', 0)
                    ])
                
                print_stats(f"📚 Latency history logged: avg {avg_latency:.3f}ms, {pair_count} pairs")
                
                # Log significant latency events
                if avg_latency > 5:
                    self._log_event(f"HIGH LATENCY: avg {avg_latency:.2f}ms, max {max_latency:.2f}ms", "WARNING")
                
        except Exception as e:
            print_error(f"❌ Error logging latency history: {e}")
    
    def _log_health_history(self, health_data):
        """Log network health statistics to history file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.health_history, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    health_data.get('link_health', 0),
                    health_data.get('connectivity_health', 0),
                    health_data.get('total_links', 0),
                    health_data.get('links_up', 0),
                    health_data.get('overall_status', 'Unknown')
                ])
            
            # Log health issues
            if health_data.get('link_health', 100) < 100:
                self._log_event(f"NETWORK ISSUE: Link health {health_data.get('link_health')}%", "WARNING")
            
        except Exception as e:
            print_error(f"❌ Error logging health history: {e}")
    
    def _save_stats_to_files(self):
        """Save collected statistics to current CSV files"""
        try:
            # Save traffic stats
            self._save_traffic_stats()
            
            # Save latency stats  
            self._save_latency_stats()
            
            # Save admission stats
            self._save_admission_stats()
            
            # Save link utilization stats
            self._save_link_stats()
            
        except Exception as e:
            print_error(f"⚠️ Error saving stats: {e}")
    
    def _save_traffic_stats(self):
        """Save traffic statistics to CSV"""
        traffic_file = f"{self.stats_dir}/traffic_stats.csv"
        
        with open(traffic_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'switch', 'total_packets', 'total_bytes', 'flow_count', 'avg_packet_size'])
            
            for switch, stats_list in self.traffic_stats.items():
                for stats in stats_list:
                    writer.writerow([
                        stats['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        stats['switch'],
                        stats['total_packets'],
                        stats['total_bytes'],
                        stats['flow_count'],
                        stats['avg_packet_size']
                    ])
    
    def _save_latency_stats(self):
        """Save latency statistics to CSV"""
        latency_file = f"{self.stats_dir}/latency_stats.csv"
        
        with open(latency_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'src', 'dst', 'latency_ms', 'status'])
            
            for pair, stats_list in self.latency_stats.items():
                for stats in stats_list:
                    writer.writerow([
                        stats['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        stats['src'],
                        stats['dst'],
                        stats['latency_ms'],
                        stats['status']
                    ])
    
    def _save_admission_stats(self):
        """Save admission control statistics to CSV"""
        admission_file = f"{self.stats_dir}/admission_stats.csv"
        
        with open(admission_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'total_links', 'links_up', 'link_health', 'connectivity_health', 'overall_status'])
            
            for stats in self.admission_stats:
                writer.writerow([
                    stats['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    stats['total_links'],
                    stats['links_up'],
                    stats['link_health'],
                    stats['connectivity_health'],
                    stats['overall_status']
                ])
    
    def _save_link_stats(self):
        """Save link utilization statistics to CSV"""
        link_file = f"{self.stats_dir}/link_utilization.csv"
        
        with open(link_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'link', 'status', 'utilization'])
            
            for link, stats_list in self.link_utilization.items():
                for stats in stats_list:
                    writer.writerow([
                        stats['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        stats['link'],
                        stats['status'],
                        stats['utilization']
                    ])
    
    def generate_daily_summary(self):
        """Generate daily summary from history logs"""
        try:
            summary = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': {}
            }
            
            # Analyze traffic history
            if os.path.exists(self.traffic_history):
                with open(self.traffic_history, 'r') as f:
                    reader = csv.DictReader(f)
                    traffic_rows = list(reader)
                    
                    if traffic_rows:
                        total_packets = [int(row['total_packets']) for row in traffic_rows if row['total_packets'].isdigit()]
                        summary['statistics']['traffic'] = {
                            'max_packets': max(total_packets) if total_packets else 0,
                            'avg_packets': sum(total_packets) / len(total_packets) if total_packets else 0,
                            'entries_logged': len(traffic_rows)
                        }
            
            # Analyze latency history
            if os.path.exists(self.latency_history):
                with open(self.latency_history, 'r') as f:
                    reader = csv.DictReader(f)
                    latency_rows = list(reader)
                    
                    if latency_rows:
                        avg_latencies = [float(row['avg_latency']) for row in latency_rows 
                                       if row['avg_latency'] and float(row['avg_latency']) > 0]
                        summary['statistics']['latency'] = {
                            'best_avg': min(avg_latencies) if avg_latencies else 0,
                            'worst_avg': max(avg_latencies) if avg_latencies else 0,
                            'overall_avg': sum(avg_latencies) / len(avg_latencies) if avg_latencies else 0,
                            'entries_logged': len(latency_rows)
                        }
            
            # Save summary
            with open(self.daily_summary, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print_important(f"📊 Daily summary generated: {self.daily_summary}")
            return summary
            
        except Exception as e:
            print_error(f"❌ Error generating daily summary: {e}")
            return None
    
    def generate_report(self):
        """Generate a comprehensive report"""
        print_important("\n📊 NETWORK STATISTICS SUMMARY (REAL MEASUREMENTS + HISTORY)")
        print_important("=" * 65)
        
        # Current stats
        if self.latency_stats:
            print_important("\n⏱️ Current Latency Statistics (REAL PING MEASUREMENTS):")
            total_measurements = 0
            for pair, stats_list in self.latency_stats.items():
                if stats_list:
                    recent_latencies = [s['latency_ms'] for s in list(stats_list)[-5:] 
                                      if s['latency_ms'] and s['latency_ms'] > 0 and s['status'] == 'real_ping']
                    if recent_latencies:
                        avg_latency = sum(recent_latencies) / len(recent_latencies)
                        min_latency = min(recent_latencies)
                        max_latency = max(recent_latencies)
                        measurement_count = len(recent_latencies)
                        total_measurements += measurement_count
                        print_important(f"   {pair}: avg={avg_latency:.3f}ms, min={min_latency:.3f}ms, max={max_latency:.3f}ms ({measurement_count} measurements)")
        
        # History log status
        print_important(f"\n📚 History Log Files:")
        history_files = [
            ('Traffic History', self.traffic_history),
            ('Latency History', self.latency_history),
            ('Health History', self.health_history),
            ('Events Log', self.events_log)
        ]
        
        for name, filepath in history_files:
            if os.path.exists(filepath):
                try:
                    if filepath.endswith('.csv'):
                        with open(filepath, 'r') as f:
                            lines = len(f.readlines()) - 1  # Exclude header
                        print_important(f"   ✅ {name}: {lines} entries")
                    else:
                        with open(filepath, 'r') as f:
                            lines = len(f.readlines())
                        print_important(f"   ✅ {name}: {lines} log entries")
                except:
                    print_important(f"   ⚠️ {name}: exists but unreadable")
            else:
                print_important(f"   ❌ {name}: not found")
        
        print_important(f"\n📁 Current stats saved to: {self.stats_dir}/")
        print_important(f"📚 History logs saved to: {self.logs_dir}/")
        print_important(f"🎯 All latency measurements are REAL ping results")
    
    def get_real_time_stats(self):
        """Get current real-time statistics"""
        stats = {}
        
        # Current traffic
        if self.traffic_stats:
            stats['traffic'] = {}
            for switch, stats_list in self.traffic_stats.items():
                if stats_list:
                    stats['traffic'][switch] = stats_list[-1]
        
        # Current latency - REAL MEASUREMENTS ONLY
        if self.latency_stats:
            stats['latency'] = {}
            stats['latency_count'] = 0
            for pair, stats_list in self.latency_stats.items():
                if stats_list:
                    # Only include real ping measurements
                    recent_real = [s for s in list(stats_list)[-5:] 
                                  if s['latency_ms'] and s['latency_ms'] > 0 and s['status'] == 'real_ping']
                    if recent_real:
                        avg_latency = sum(s['latency_ms'] for s in recent_real) / len(recent_real)
                        stats['latency'][pair] = avg_latency
                        stats['latency_count'] += len(recent_real)
        
        return stats
    
    def test_dashboard_connectivity(self):
        """Test if dashboard communication is working"""
        try:
            print_stats("🧪 Testing dashboard connectivity...")
            
            # Test basic dashboard connection
            response = requests.get('http://localhost:5000/api/status', timeout=3)
            if response.status_code == 200:
                print_stats("✅ Dashboard is accessible")
                
                # Test ping command
                ping_response = requests.post('http://localhost:5000/api/execute',
                                            json={'command': 'h1 ping -c 1 h3'},
                                            timeout=8)
                if ping_response.status_code == 200:
                    result = ping_response.json()
                    if result.get('success'):
                        print_stats("✅ Dashboard ping commands work")
                        if 'time=' in result.get('output', ''):
                            print_stats("✅ Ping latency measurement available")
                            return True
                        else:
                            print_stats("⚠️ Ping works but no latency info")
                    else:
                        print_stats("❌ Dashboard ping commands failed")
                else:
                    print_stats("❌ Dashboard ping request failed")
            else:
                print_stats("❌ Dashboard not accessible")
            
            return False
            
        except Exception as e:
            print_error(f"❌ Dashboard connectivity test failed: {e}")
            return False

def main():
    """Standalone monitoring script with history logging"""
    print_important("🚀 Network Statistics Monitor - REAL PING + HISTORY LOGGING")
    print_important("=" * 65)
    print_important("🎯 This version records real ping results AND maintains history logs")
    print_important("📚 Creates detailed history files for analysis")
    print_important("📊 All latency measurements are real network measurements")
    
    monitor = NetworkStatsMonitor(monitor_interval=10)  # Longer interval for real pings
    
    # Test dashboard connectivity first
    if not monitor.test_dashboard_connectivity():
        print_important("\n❌ Dashboard connectivity test failed!")
        print_important("Please ensure:")
        print_important("1. Dashboard is running: python3 working_dashboard.py")
        print_important("2. Controller is connected to dashboard")
        print_important("3. Network is initialized")
        print_important("\nStarting monitor anyway (will show warnings)...")
    
    try:
        monitor.start_monitoring()
        
        print_important("\n💡 Commands:")
        print_important("   Press 'r' + Enter for real-time report")
        print_important("   Press 's' + Enter for summary")
        print_important("   Press 'l' + Enter to check latency files")
        print_important("   Press 'h' + Enter to check history logs")
        print_important("   Press 'd' + Enter to generate daily summary")
        print_important("   Press 't' + Enter to test dashboard connectivity")
        print_important("   Press 'q' + Enter to quit")
        
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd == 'r':
                monitor.generate_report()
            elif cmd == 's':
                stats = monitor.get_real_time_stats()
                print_important(f"\n📊 Real-time stats: {len(stats)} categories collected")
                if 'latency' in stats and stats['latency']:
                    print_important(f"⏱️ Current average latencies ({stats.get('latency_count', 0)} real measurements):")
                    for pair, latency in stats['latency'].items():
                        print_important(f"   {pair}: {latency:.3f}ms")
                else:
                    print_important("⚠️ No real latency measurements available")
            elif cmd == 'l':
                # Check current latency file
                latency_file = f"{monitor.stats_dir}/latency_stats.csv"
                if os.path.exists(latency_file):
                    with open(latency_file, 'r') as f:
                        lines = f.readlines()
                        print_important(f"\n📁 Current latency file: {len(lines)-1} entries")
                        if len(lines) > 1:
                            print_important("Recent REAL ping measurements:")
                            for line in lines[-5:]:
                                if 'real_ping' in line:
                                    parts = line.strip().split(',')
                                    if len(parts) >= 4:
                                        print_important(f"   {parts[1]}→{parts[2]}: {parts[3]}ms ({parts[0]})")
                        else:
                            print_important("   No data entries yet")
                else:
                    print_important(f"\n📁 Current latency file not found: {latency_file}")
            elif cmd == 'h':
                # Check history logs
                print_important(f"\n📚 History Log Status:")
                history_files = [
                    ('Traffic History', monitor.traffic_history),
                    ('Latency History', monitor.latency_history),
                    ('Health History', monitor.health_history),
                    ('Events Log', monitor.events_log)
                ]
                
                for name, filepath in history_files:
                    if os.path.exists(filepath):
                        try:
                            with open(filepath, 'r') as f:
                                lines = f.readlines()
                                if filepath.endswith('.csv'):
                                    entry_count = len(lines) - 1  # Exclude header
                                    print_important(f"   ✅ {name}: {entry_count} entries")
                                    if len(lines) > 1:
                                        print_important(f"      Latest: {lines[-1].strip()}")
                                else:
                                    entry_count = len(lines)
                                    print_important(f"   ✅ {name}: {entry_count} log entries")
                                    if lines:
                                        print_important(f"      Latest: {lines[-1].strip()}")
                        except Exception as e:
                            print_important(f"   ⚠️ {name}: Error reading - {e}")
                    else:
                        print_important(f"   ❌ {name}: Not found")
            elif cmd == 'd':
                # Generate daily summary
                summary = monitor.generate_daily_summary()
                if summary:
                    print_important(f"\n📊 Daily Summary Generated:")
                    print_important(f"   Date: {summary['date']}")
                    if 'statistics' in summary:
                        stats = summary['statistics']
                        if 'traffic' in stats:
                            print_important(f"   Traffic: {stats['traffic']['entries_logged']} entries, max {stats['traffic']['max_packets']} packets")
                        if 'latency' in stats:
                            print_important(f"   Latency: {stats['latency']['entries_logged']} entries, avg {stats['latency']['overall_avg']:.3f}ms")
                    print_important(f"   File: {monitor.daily_summary}")
                else:
                    print_important("❌ Failed to generate daily summary")
            elif cmd == 't':
                monitor.test_dashboard_connectivity()
            else:
                print_important("Unknown command. Use 'r', 's', 'l', 'h', 'd', 't', or 'q'.")
    
    except KeyboardInterrupt:
        print_important("\n🛑 Interrupted by user")
    
    finally:
        monitor.stop_monitoring()
        monitor.generate_report()
        monitor.container_addon.cleanup_all()

        # Generate final daily summary
        print_important("\n📊 Generating final daily summary...")
        monitor.generate_daily_summary()
        
        print_important("👋 Monitoring stopped. Real ping measurements and history logs saved.")
        print_important(f"📁 Current stats: {monitor.stats_dir}/")
        print_important(f"📚 History logs: {monitor.logs_dir}/")
        print_important("🎯 Only real latency measurements recorded - no simulation used!")

if __name__ == '__main__':
    main()
