#!/usr/bin/env python3
"""
network_logger.py
Logs network statistics and events to files for historical analysis
"""

import os
import csv
import json
import time
from datetime import datetime
import threading

class NetworkLogger:
    """Logs network data to various file formats for historical analysis"""
    
    def __init__(self, log_dir='./network_logs'):
        self.log_dir = log_dir
        self.ensure_log_directory()
        
        # CSV files for different data types
        self.traffic_log = os.path.join(log_dir, 'traffic_history.csv')
        self.latency_log = os.path.join(log_dir, 'latency_history.csv')
        self.health_log = os.path.join(log_dir, 'health_history.csv')
        self.events_log = os.path.join(log_dir, 'events.log')
        self.daily_summary = os.path.join(log_dir, f'daily_summary_{datetime.now().strftime("%Y%m%d")}.json')
        
        # Initialize CSV files with headers
        self._initialize_csv_files()
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        print(f"📝 Network logger initialized")
        print(f"📁 Log directory: {log_dir}")
    
    def ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"📁 Created log directory: {self.log_dir}")
    
    def _initialize_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        
        # Traffic log headers
        if not os.path.exists(self.traffic_log):
            with open(self.traffic_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'total_packets', 'total_bytes', 'total_flows', 
                               'avg_packet_size', 'busiest_switch', 'es1_packets', 'es2_packets', 
                               'es3_packets', 'es4_packets'])
        
        # Latency log headers
        if not os.path.exists(self.latency_log):
            with open(self.latency_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'avg_latency', 'min_latency', 'max_latency', 
                               'pair_count', 'h1_h3', 'h1_h5', 'h1_h7', 'h3_h5', 'h3_h7', 
                               'h5_h7', 'h2_h6', 'h4_h8'])
        
        # Health log headers
        if not os.path.exists(self.health_log):
            with open(self.health_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'link_health', 'connectivity_health', 
                               'total_links', 'links_up', 'overall_status'])
    
    def log_traffic_data(self, traffic_data):
        """Log traffic statistics to CSV"""
        try:
            with self.lock:
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
                
                with open(self.traffic_log, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp, total_packets, total_bytes, total_flows, 
                        avg_packet_size, busiest_switch,
                        switch_packets.get('es1_packets', 0),
                        switch_packets.get('es2_packets', 0),
                        switch_packets.get('es3_packets', 0),
                        switch_packets.get('es4_packets', 0)
                    ])
                
                # Also log to events
                self.log_event(f"Traffic: {total_packets} packets, {total_bytes} bytes, busiest: {busiest_switch}")
                
        except Exception as e:
            print(f"❌ Error logging traffic data: {e}")
    
    def log_latency_data(self, latency_data):
        """Log latency statistics to CSV"""
        try:
            with self.lock:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if latency_data:
                    latencies = [v for v in latency_data.values() if v > 0]
                    avg_latency = sum(latencies) / len(latencies) if latencies else 0
                    min_latency = min(latencies) if latencies else 0
                    max_latency = max(latencies) if latencies else 0
                    pair_count = len(latencies)
                    
                    with open(self.latency_log, 'a', newline='') as f:
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
                    
                    # Log significant latency events
                    if avg_latency > 20:
                        self.log_event(f"HIGH LATENCY: avg {avg_latency:.2f}ms, max {max_latency:.2f}ms", level="WARNING")
                    elif avg_latency > 0:
                        self.log_event(f"Latency: avg {avg_latency:.2f}ms, {pair_count} pairs")
                
        except Exception as e:
            print(f"❌ Error logging latency data: {e}")
    
    def log_health_data(self, health_data):
        """Log network health statistics to CSV"""
        try:
            with self.lock:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(self.health_log, 'a', newline='') as f:
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
                    self.log_event(f"NETWORK ISSUE: Link health {health_data.get('link_health')}%", level="WARNING")
                
        except Exception as e:
            print(f"❌ Error logging health data: {e}")
    
    def log_event(self, message, level="INFO"):
        """Log events to text file"""
        try:
            with self.lock:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] [{level}] {message}\n"
                
                with open(self.events_log, 'a') as f:
                    f.write(log_entry)
                
        except Exception as e:
            print(f"❌ Error logging event: {e}")
    
    def log_command_execution(self, command, success, output=""):
        """Log command executions"""
        status = "SUCCESS" if success else "FAILED"
        self.log_event(f"COMMAND {status}: {command} | {output[:100]}...")
    
    def generate_daily_summary(self):
        """Generate daily summary from logs"""
        try:
            summary = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': {}
            }
            
            # Analyze traffic log
            if os.path.exists(self.traffic_log):
                with open(self.traffic_log, 'r') as f:
                    reader = csv.DictReader(f)
                    traffic_rows = list(reader)
                    
                    if traffic_rows:
                        total_packets = [int(row['total_packets']) for row in traffic_rows if row['total_packets'].isdigit()]
                        summary['statistics']['traffic'] = {
                            'max_packets': max(total_packets) if total_packets else 0,
                            'avg_packets': sum(total_packets) / len(total_packets) if total_packets else 0,
                            'entries_logged': len(traffic_rows)
                        }
            
            # Analyze latency log
            if os.path.exists(self.latency_log):
                with open(self.latency_log, 'r') as f:
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
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generating daily summary: {e}")
            return None
    
    def get_recent_data(self, hours=1):
        """Get recent data from logs"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            recent_data = {
                'traffic': [],
                'latency': [],
                'health': [],
                'events': []
            }
            
            # Get recent traffic data
            if os.path.exists(self.traffic_log):
                with open(self.traffic_log, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            row_time = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp()
                            if row_time > cutoff_time:
                                recent_data['traffic'].append(row)
                        except:
                            continue
            
            # Get recent latency data
            if os.path.exists(self.latency_log):
                with open(self.latency_log, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            row_time = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp()
                            if row_time > cutoff_time:
                                recent_data['latency'].append(row)
                        except:
                            continue
            
            # Get recent events
            if os.path.exists(self.events_log):
                with open(self.events_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-100:]:  # Last 100 events
                        recent_data['events'].append(line.strip())
            
            return recent_data
            
        except Exception as e:
            print(f"❌ Error getting recent data: {e}")
            return None
    
    def cleanup_old_logs(self, days=7):
        """Clean up logs older than specified days"""
        try:
            cutoff = time.time() - (days * 24 * 3600)
            
            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff:
                        os.remove(filepath)
                        print(f"🗑️ Removed old log file: {filename}")
            
        except Exception as e:
            print(f"❌ Error cleaning up logs: {e}")

# Integration function for dashboard
def add_logging_to_dashboard_core():
    """Add logging functionality to the dashboard core"""
    logger = NetworkLogger()
    
    # Log startup
    logger.log_event("Dashboard Core Started", level="INFO")
    
    return logger

# Utility functions for log analysis
def analyze_logs(log_dir='./network_logs'):
    """Analyze network logs and provide insights"""
    try:
        traffic_log = os.path.join(log_dir, 'traffic_history.csv')
        latency_log = os.path.join(log_dir, 'latency_history.csv')
        
        analysis = {
            'traffic_analysis': {},
            'latency_analysis': {},
            'recommendations': []
        }
        
        # Analyze traffic patterns
        if os.path.exists(traffic_log):
            with open(traffic_log, 'r') as f:
                reader = csv.DictReader(f)
                traffic_data = list(reader)
                
                if traffic_data:
                    packets = [int(row['total_packets']) for row in traffic_data if row['total_packets'].isdigit()]
                    analysis['traffic_analysis'] = {
                        'total_entries': len(traffic_data),
                        'max_packets': max(packets) if packets else 0,
                        'min_packets': min(packets) if packets else 0,
                        'avg_packets': sum(packets) / len(packets) if packets else 0,
                        'trend': 'increasing' if len(packets) >= 2 and packets[-1] > packets[0] else 'stable'
                    }
        
        # Analyze latency patterns
        if os.path.exists(latency_log):
            with open(latency_log, 'r') as f:
                reader = csv.DictReader(f)
                latency_data = list(reader)
                
                if latency_data:
                    latencies = [float(row['avg_latency']) for row in latency_data 
                               if row['avg_latency'] and float(row['avg_latency']) > 0]
                    analysis['latency_analysis'] = {
                        'total_entries': len(latency_data),
                        'best_latency': min(latencies) if latencies else 0,
                        'worst_latency': max(latencies) if latencies else 0,
                        'avg_latency': sum(latencies) / len(latencies) if latencies else 0,
                        'performance': 'excellent' if sum(latencies) / len(latencies) < 5 else 'good' if sum(latencies) / len(latencies) < 15 else 'poor'
                    }
        
        # Generate recommendations
        if analysis['latency_analysis'].get('avg_latency', 0) > 20:
            analysis['recommendations'].append("High latency detected - check network congestion")
        
        if analysis['traffic_analysis'].get('trend') == 'increasing':
            analysis['recommendations'].append("Traffic trend is increasing - monitor capacity")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")
        return None

def get_log_file_paths(log_dir='./network_logs'):
    """Get paths to all log files"""
    files = {
        'traffic_history': os.path.join(log_dir, 'traffic_history.csv'),
        'latency_history': os.path.join(log_dir, 'latency_history.csv'),
        'health_history': os.path.join(log_dir, 'health_history.csv'),
        'events_log': os.path.join(log_dir, 'events.log'),
        'daily_summary': os.path.join(log_dir, f'daily_summary_{datetime.now().strftime("%Y%m%d")}.json')
    }
    
    # Check which files exist
    existing_files = {name: path for name, path in files.items() if os.path.exists(path)}
    
    return existing_files

if __name__ == '__main__':
    # Test the logger
    print("🧪 Testing Network Logger")
    
    logger = NetworkLogger()
    
    # Test logging
    sample_traffic = {
        'es1': {'total_packets': 100, 'total_bytes': 8500, 'flow_count': 2},
        'es2': {'total_packets': 150, 'total_bytes': 12000, 'flow_count': 3},
        'es3': {'total_packets': 200, 'total_bytes': 15000, 'flow_count': 4},
        'es4': {'total_packets': 80, 'total_bytes': 6500, 'flow_count': 1}
    }
    
    sample_latency = {
        'h1-h3': 2.5, 'h1-h5': 8.2, 'h1-h7': 9.1,
        'h3-h5': 7.8, 'h3-h7': 8.9, 'h5-h7': 3.1
    }
    
    sample_health = {
        'link_health': 100, 'connectivity_health': 100,
        'total_links': 20, 'links_up': 20, 'overall_status': '🟢 HEALTHY'
    }
    
    logger.log_traffic_data(sample_traffic)
    logger.log_latency_data(sample_latency)
    logger.log_health_data(sample_health)
    logger.log_event("Test event logged successfully")
    
    # Generate summary
    summary = logger.generate_daily_summary()
    print(f"📊 Daily summary generated: {summary}")
    
    # Show log file paths
    files = get_log_file_paths()
    print(f"\n📁 Log files created:")
    for name, path in files.items():
        print(f"   {name}: {path}")
    
    # Analyze logs
    analysis = analyze_logs()
    print(f"\n📈 Log analysis: {analysis}")
    
    print(f"\n✅ Logger test complete!")
