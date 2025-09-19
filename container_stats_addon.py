#!/usr/bin/env python3
"""
container_stats_addon.py
Add-on to monitor Alpine containers on h1 and h3 with history logging
UPDATED VERSION with MONITORING TOGGLE and FIXED MEMORY PARSING
"""

import subprocess
import time
import csv
import os
import re
from datetime import datetime

# NEW: Import monitoring toggle
from monitoring_toggle import print_container, print_important, print_error

def parse_memory_value_for_csv(memory_str):
    """Parse memory values like '3.57k', '2.4MiB' and convert to MB for CSV storage"""
    if not memory_str or memory_str == '0' or memory_str == '':
        return 0.0
    
    memory_str = str(memory_str).strip()
    
    # Handle plain numbers first (assume MB)
    try:
        return float(memory_str)
    except:
        pass
    
    # Handle units with regex - FIXED PARSING
    match = re.match(r'([0-9.]+)([kmgtKMGT]?i?[Bb]?)', memory_str.lower())
    if match:
        value_str, unit = match.groups()
        try:
            value = float(value_str)
            unit = unit.lower().replace('ib', '').replace('b', '')  # Remove 'iB' or 'B' suffixes
            
            # Convert to MB properly
            if unit in ['k', 'ki']:
                return value / 1024  # KB to MB: divide by 1024
            elif unit in ['m', 'mi', '']:
                return value  # Already MB or assume MB
            elif unit in ['g', 'gi']:
                return value * 1024  # GB to MB
            elif unit in ['t', 'ti']:
                return value * 1024 * 1024  # TB to MB
            else:
                return value  # Unknown unit, return as-is
        except ValueError:
            print_error(f"Warning: Could not parse memory numeric part: '{value_str}' from '{memory_str}'")
            return 0.0
    
    print_error(f"Warning: Could not parse memory value: '{memory_str}'")
    return 0.0

def parse_cpu_percent_for_csv(cpu_str):
    """Parse CPU percentage values for CSV storage"""
    if not cpu_str or cpu_str == '0' or cpu_str == '':
        return 0.0
    
    try:
        # Remove % symbol and any whitespace
        cpu_str = str(cpu_str).replace('%', '').strip()
        return float(cpu_str)
    except ValueError:
        print_error(f"Warning: Could not parse CPU value: '{cpu_str}'")
        return 0.0

def parse_network_value(net_str):
    """Parse network values like '1.2MB', '500kB' to MB"""
    if not net_str or net_str == '0' or net_str == '':
        return 0.0
    
    net_str = str(net_str).strip()
    
    # Handle plain numbers first (assume MB)
    try:
        return float(net_str)
    except:
        pass
    
    # Handle units with regex
    match = re.match(r'([0-9.]+)([kmgtKMGT]?[Bb]?)', net_str.lower())
    if match:
        value_str, unit = match.groups()
        try:
            value = float(value_str)
            unit = unit.lower().replace('b', '')  # Remove 'B' suffix
            
            # Convert to MB
            if unit == 'k':
                return value / 1024  # KB to MB
            elif unit == 'm' or unit == '':
                return value  # Already MB or assume MB
            elif unit == 'g':
                return value * 1024  # GB to MB
            else:
                return value  # Unknown unit, return as-is
        except ValueError:
            return 0.0
    
    return 0.0

class ContainerStatsAddon:
    """Separate container monitoring addon with history logging and FIXED parsing"""
    
    def __init__(self, stats_dir='./network_stats'):
        self.stats_dir = stats_dir
        self.container_file = f"{stats_dir}/container_stats.csv"
        self.container_history = f"./network_logs/container_history.csv"
        self.init_csv()
    
    def init_csv(self):
        """Initialize container stats CSV files"""
        # Create stats directory
        os.makedirs(self.stats_dir, exist_ok=True)
        
        # Current stats
        if not os.path.exists(self.container_file):
            with open(self.container_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'host', 'container_name', 'status', 'cpu_percent', 'memory_mb', 'network_rx_mb', 'network_tx_mb'])
        
        # History log
        os.makedirs('./network_logs', exist_ok=True)
        if not os.path.exists(self.container_history):
            with open(self.container_history, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'total_containers', 'running_containers', 'avg_cpu_percent', 'total_memory_mb', 'h1_status', 'h3_status', 'h1_cpu', 'h3_cpu', 'h1_memory', 'h3_memory'])
    
    def start_containers(self):
        """Start Alpine containers (fixed version)"""
        try:
            # Remove any existing containers first
            subprocess.run("docker rm -f alpine_h1 alpine_h3 2>/dev/null", shell=True)
            
            # Start containers normally (without netns)
            cmd_h1 = "docker run -d --name alpine_h1 alpine:latest sleep 3600"
            cmd_h3 = "docker run -d --name alpine_h3 alpine:latest sleep 3600"
            
            result1 = subprocess.run(cmd_h1, shell=True, capture_output=True, text=True)
            result2 = subprocess.run(cmd_h3, shell=True, capture_output=True, text=True)
            
            if result1.returncode == 0 and result2.returncode == 0:
                print_important("✅ Alpine containers started on h1 and h3")
                
                # Verify they're running
                time.sleep(2)
                check_result = subprocess.run("docker ps | grep alpine_", shell=True, capture_output=True, text=True)
                if "alpine_h1" in check_result.stdout and "alpine_h3" in check_result.stdout:
                    print_important("✅ Containers verified running")
                    return True
                else:
                    print_error("⚠️ Containers started but not running properly")
                    return False
            else:
                print_error(f"❌ Container start failed:")
                if result1.returncode != 0:
                    print_error(f"   h1 error: {result1.stderr}")
                if result2.returncode != 0:
                    print_error(f"   h3 error: {result2.stderr}")
                return False
                
        except Exception as e:
            print_error(f"❌ Container start failed: {e}")
            return False
    
    def collect_container_stats(self):
        """Collect stats from both containers with FIXED parsing"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        container_data = {}
        
        for host, container in [('h1', 'alpine_h1'), ('h3', 'alpine_h3')]:
            try:
                # Check if container exists and is running
                check_cmd = f"docker ps --filter name={container} --format '{{{{.Names}}}}'"
                check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                
                if container in check_result.stdout:
                    # Container is running, get stats
                    stats_cmd = f"docker stats {container} --no-stream --format '{{{{.CPUPerc}}}}|{{{{.MemUsage}}}}|{{{{.NetIO}}}}'"
                    result = subprocess.run(stats_cmd, shell=True, capture_output=True, text=True, timeout=5)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        data = result.stdout.strip().split('|')
                        
                        # FIXED: Properly parse and convert values
                        cpu_raw = data[0].strip() if len(data) > 0 else '0%'
                        mem_raw = data[1].split('/')[0].strip() if len(data) > 1 else '0MiB'
                        net_parts = data[2].split('/') if len(data) > 2 else ['0B', '0B']
                        net_rx_raw = net_parts[0].strip()
                        net_tx_raw = net_parts[1].strip()
                        
                        # Convert using FIXED parsing functions
                        cpu_mb = parse_cpu_percent_for_csv(cpu_raw)
                        mem_mb = parse_memory_value_for_csv(mem_raw)
                        net_rx_mb = parse_network_value(net_rx_raw)
                        net_tx_mb = parse_network_value(net_tx_raw)
                        
                        container_data[host] = {
                            'status': 'running', 
                            'cpu': cpu_mb, 
                            'memory': mem_mb, 
                            'net_rx': net_rx_mb, 
                            'net_tx': net_tx_mb
                        }
                        
                        # Write to current CSV with CONVERTED values (not raw strings)
                        with open(self.container_file, 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([timestamp, host, container, 'running', cpu_mb, mem_mb, net_rx_mb, net_tx_mb])
                        
                        # Show what was parsed
                        print_container(f"📊 {host}/{container}: CPU {cpu_mb:.1f}%, MEM {mem_mb:.3f}MB (from '{cpu_raw}'->'{mem_raw}')")
                    else:
                        # Stats command failed
                        container_data[host] = {'status': 'error', 'cpu': 0.0, 'memory': 0.0, 'net_rx': 0.0, 'net_tx': 0.0}
                        with open(self.container_file, 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([timestamp, host, container, 'error', 0.0, 0.0, 0.0, 0.0])
                else:
                    # Container not running
                    container_data[host] = {'status': 'stopped', 'cpu': 0.0, 'memory': 0.0, 'net_rx': 0.0, 'net_tx': 0.0}
                    with open(self.container_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, host, container, 'stopped', 0.0, 0.0, 0.0, 0.0])
                        
            except Exception as e:
                print_error(f"⚠️ Error collecting {host} stats: {e}")
                container_data[host] = {'status': 'error', 'cpu': 0.0, 'memory': 0.0, 'net_rx': 0.0, 'net_tx': 0.0}
        
        # Write to history log
        self._log_container_history(timestamp, container_data)
    
    def _log_container_history(self, timestamp, container_data):
        """Log aggregated container history with FIXED values"""
        try:
            total_containers = len(container_data)
            running_containers = sum(1 for data in container_data.values() if data['status'] == 'running')
            
            # Calculate averages using FIXED numeric values
            cpus = []
            memories = []
            for data in container_data.values():
                if isinstance(data['cpu'], (int, float)) and data['cpu'] > 0:
                    cpus.append(data['cpu'])
                if isinstance(data['memory'], (int, float)) and data['memory'] > 0:
                    memories.append(data['memory'])
            
            avg_cpu = sum(cpus) / len(cpus) if cpus else 0.0
            total_memory = sum(memories) if memories else 0.0
            
            # Individual container data
            h1_data = container_data.get('h1', {'status': 'unknown', 'cpu': 0.0, 'memory': 0.0})
            h3_data = container_data.get('h3', {'status': 'unknown', 'cpu': 0.0, 'memory': 0.0})
            
            with open(self.container_history, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, total_containers, running_containers, 
                    round(avg_cpu, 2), round(total_memory, 3),  # More precision for memory
                    h1_data['status'], h3_data['status'], 
                    round(h1_data['cpu'], 2), round(h3_data['cpu'], 2),
                    round(h1_data['memory'], 3), round(h3_data['memory'], 3)
                ])
            
            if running_containers > 0:
                print_container(f"📚 Container history: {running_containers}/{total_containers} running, avg CPU {avg_cpu:.1f}%, total MEM {total_memory:.1f}MB")
            
        except Exception as e:
            print_error(f"❌ Error logging container history: {e}")
    
    def stop_containers(self):
        """Stop and remove containers"""
        try:
            subprocess.run("docker stop alpine_h1 alpine_h3 2>/dev/null", shell=True)
            subprocess.run("docker rm alpine_h1 alpine_h3 2>/dev/null", shell=True)
            print_important("🛑 Containers stopped and removed")
        except:
            pass
    
    def cleanup_all(self):
        """Complete cleanup - containers, stats files, everything"""
        try:
            # Stop and remove containers
            subprocess.run("docker stop alpine_h1 alpine_h3 2>/dev/null", shell=True)
            subprocess.run("docker rm alpine_h1 alpine_h3 2>/dev/null", shell=True)
            
            # Remove container stats file
            if os.path.exists(self.container_file):
                os.remove(self.container_file)
                print_important("🗑️ Container stats file removed")
            
            # Remove container history file
            if os.path.exists(self.container_history):
                os.remove(self.container_history)
                print_important("🗑️ Container history file removed")
            
            # Clean up any orphaned containers
            subprocess.run("docker container prune -f 2>/dev/null", shell=True)
            
            print_important("🧹 Complete container cleanup done")
        except Exception as e:
            print_error(f"⚠️ Cleanup warning: {e}")
    
    def get_container_status(self):
        """Get current container status for reporting"""
        try:
            result = subprocess.run("docker ps --filter name=alpine_ --format '{{.Names}} {{.Status}}'", 
                                   shell=True, capture_output=True, text=True)
            
            status_info = {}
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            container_name = parts[0]
                            status = parts[1]
                            if 'alpine_h1' in container_name:
                                status_info['h1'] = 'running'
                            elif 'alpine_h3' in container_name:
                                status_info['h3'] = 'running'
            
            # Default to stopped for any missing containers
            if 'h1' not in status_info:
                status_info['h1'] = 'stopped'
            if 'h3' not in status_info:
                status_info['h3'] = 'stopped'
            
            return status_info
            
        except Exception as e:
            print_error(f"⚠️ Error getting container status: {e}")
            return {'h1': 'unknown', 'h3': 'unknown'}

def test_parsing_functions():
    """Test the parsing functions to verify they work correctly"""
    print_important("\n🧪 Testing FIXED parsing functions:")
    print_important("=" * 40)
    
    # Test memory parsing
    memory_tests = ['3.57k', '2.4MiB', '1.5MB', '100', '1.2GiB', '0', '']
    print_important("Memory parsing tests:")
    for test_val in memory_tests:
        result = parse_memory_value_for_csv(test_val)
        print_important(f"  '{test_val:>8}' → {result:>8.3f} MB")
    
    # Test CPU parsing  
    cpu_tests = ['1.23%', '45.7%', '0.1%', '100%', '0', '']
    print_important("\nCPU parsing tests:")
    for test_val in cpu_tests:
        result = parse_cpu_percent_for_csv(test_val)
        print_important(f"  '{test_val:>8}' → {result:>6.1f}%")
    
    # Test network parsing
    net_tests = ['1.2MB', '500kB', '1.5GB', '0B', '100', '']
    print_important("\nNetwork parsing tests:")
    for test_val in net_tests:
        result = parse_network_value(test_val)
        print_important(f"  '{test_val:>8}' → {result:>8.3f} MB")
    
    print_important("=" * 40)
    print_important("✅ All parsing tests completed!")

def add_container_monitoring_to_existing_monitor():
    """Instructions to add container monitoring to existing monitor"""
    print_important("🔧 Add Container Monitoring to Your Existing Monitor")
    print_important("=" * 50)
    print_important()
    print_important("Add this to your NetworkStatsMonitor.__init__() AFTER self.stats_dir is set:")
    print_important("    from container_stats_addon import ContainerStatsAddon")
    print_important("    self.container_addon = ContainerStatsAddon(self.stats_dir)")
    print_important()
    print_important("Add this to your _monitoring_loop() after existing collections:")
    print_important("    self.container_addon.collect_container_stats()")
    print_important()
    print_important("Add this to your stop_monitoring():")
    print_important("    self.container_addon.cleanup_all()  # Full cleanup on exit")

def add_cleanup_to_controller():
    """Add cleanup to your main controller"""
    print_important("\n🧹 Add Cleanup to Your Main Controller")
    print_important("=" * 40)
    print_important()
    print_important("Add this to your controller's cleanup_network() method:")
    print_important("    from container_stats_addon import ContainerStatsAddon")
    print_important("    addon = ContainerStatsAddon()")
    print_important("    addon.cleanup_all()")
    print_important()
    print_important("Or add this to the CLI exit handler in main_controller.py:")
    print_important("    try:")
    print_important("        CLI(controller.net)")
    print_important("    finally:")
    print_important("        # Your existing cleanup")
    print_important("        controller.cleanup_network()")
    print_important("        # Add container cleanup")
    print_important("        from container_stats_addon import ContainerStatsAddon")
    print_important("        ContainerStatsAddon().cleanup_all()")

if __name__ == '__main__':
    print_important("🐳 Container Stats Addon - FIXED VERSION with Proper Memory Parsing")
    print_important("=" * 65)
    
    # Test parsing functions first
    test_parsing_functions()
    
    addon = ContainerStatsAddon()
    
    print_important("\nStarting Alpine containers...")
    if addon.start_containers():
        try:
            print_important("Collecting stats every 5 seconds. Press Ctrl+C to stop.")
            print_important("Files created:")
            print_important(f"  📊 Current: {addon.container_file}")
            print_important(f"  📚 History: {addon.container_history}")
            print_important("")
            print_important("✅ FIXED: Memory values like '3.57k' are now properly converted to MB before storing in CSV")
            print_important("✅ Dashboard should no longer show 'could not convert string to float' errors")
            print_important("")
            print_important("💡 Container stats messages can be toggled with:")
            print_important("   py net.controller.enable_verbose_monitoring()  # Show messages")
            print_important("   py net.controller.disable_verbose_monitoring() # Hide messages")
            
            while True:
                addon.collect_container_stats()
                time.sleep(5)
        except KeyboardInterrupt:
            print_important("\n🛑 Stopping...")
        finally:
            addon.stop_containers()
    else:
        print_error("❌ Failed to start containers")
        print_important("Check:")
        print_important("  1. Docker is installed and running")
        print_important("  2. No existing containers with same names")
        print_important("  3. Docker permissions are correct")
