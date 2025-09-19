#!/usr/bin/env python3
"""
real_latency_only_fix.py
REAL PING MEASUREMENTS ONLY - No simulation fallback
"""

import requests
import json
import time
import re
import os

def execute_real_ping_via_dashboard(src, dst):
    """
    Execute REAL ping command via dashboard - no simulation
    """
    try:
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
                        print(f"📊 REAL ping {src}→{dst}: {latency:.2f}ms")
                        return latency
                else:
                    print(f"⚠️ Ping {src}→{dst}: no time= in output")
            else:
                print(f"❌ Ping {src}→{dst}: command failed")
        else:
            print(f"❌ Ping {src}→{dst}: HTTP {response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Real ping failed {src}→{dst}: {e}")
        return None

def real_latency_only_for_monitor(monitor_self, timestamp):
    """
    REPLACEMENT: Only collect REAL latency measurements
    If ping fails, don't record anything (no simulation)
    """
    try:
        real_measurements = 0
        
        print("📊 Collecting REAL latency measurements only...")
        
        for src, dst in monitor_self.latency_test_pairs:
            latency = execute_real_ping_via_dashboard(src, dst)
            
            if latency is not None and latency > 0:
                monitor_self.latency_stats[f"{src}-{dst}"].append({
                    'timestamp': timestamp,
                    'src': src,
                    'dst': dst,
                    'latency_ms': latency,
                    'status': 'real_ping'
                })
                real_measurements += 1
            else:
                print(f"⚠️ Skipping {src}→{dst}: no real measurement available")
            
            # Small delay between pings
            time.sleep(0.2)
        
        if real_measurements > 0:
            print(f"✅ Collected {real_measurements} REAL latency measurements")
        else:
            print("⚠️ No real latency measurements available this cycle")
        
    except Exception as e:
        print(f"❌ Error collecting real latency: {e}")

def real_latency_only_for_dashboard():
    """
    REPLACEMENT for dashboard_utils.py - only real pings
    """
    try:
        print("📊 Getting REAL latency measurements for dashboard...")
        
        test_pairs = [
            ('h1', 'h3'), ('h1', 'h5'), ('h1', 'h7'),
            ('h3', 'h5'), ('h3', 'h7'), ('h5', 'h7'),
            ('h2', 'h4'), ('h2', 'h6'), ('h2', 'h8')
        ]
        
        latency_data = {}
        successful_pings = 0
        
        for src, dst in test_pairs:
            latency = execute_real_ping_via_dashboard(src, dst)
            if latency is not None:
                latency_data[f"{src}-{dst}"] = latency
                successful_pings += 1
            time.sleep(0.1)  # Small delay
        
        if successful_pings > 0:
            print(f"✅ Got {successful_pings} real latency measurements")
            return latency_data
        else:
            print("⚠️ No real latency measurements available - returning empty")
            return {}
        
    except Exception as e:
        print(f"❌ Error getting real latency: {e}")
        return {}

def update_network_monitor_for_real_only():
    """
    Instructions to update network_statistics_monitor.py for real pings only
    """
    print("🔧 Update network_statistics_monitor.py")
    print("=" * 40)
    print()
    print("Replace the _collect_latency_stats method with:")
    print()
    print("def _collect_latency_stats(self, timestamp):")
    print("    from real_latency_only_fix import real_latency_only_for_monitor")
    print("    return real_latency_only_for_monitor(self, timestamp)")
    print()

def update_dashboard_utils_for_real_only():
    """
    Instructions to update dashboard_utils.py for real pings only
    """
    print("🔧 Update dashboard_utils.py")
    print("=" * 30)
    print()
    print("Replace the get_real_time_latency_stats function with:")
    print()
    print("def get_real_time_latency_stats():")
    print("    from real_latency_only_fix import real_latency_only_for_dashboard")
    print("    return real_latency_only_for_dashboard()")
    print()

def test_real_pings_only():
    """
    Test real ping measurements only
    """
    print("🧪 Testing REAL Ping Measurements Only")
    print("=" * 40)
    
    test_pairs = [('h1', 'h3'), ('h1', 'h5'), ('h3', 'h7')]
    successful_pings = 0
    
    for src, dst in test_pairs:
        latency = execute_real_ping_via_dashboard(src, dst)
        if latency is not None:
            print(f"✅ {src}→{dst}: {latency:.3f}ms (REAL)")
            successful_pings += 1
        else:
            print(f"❌ {src}→{dst}: Real ping failed")
    
    print(f"\n📊 Results: {successful_pings}/{len(test_pairs)} real pings successful")
    
    if successful_pings > 0:
        print("✅ Real ping measurements are working!")
        print("You can now use real-only latency collection.")
    else:
        print("❌ No real pings working. Check:")
        print("  1. Dashboard is running on localhost:5000")
        print("  2. Controller is connected to dashboard")
        print("  3. Network hosts are reachable")
    
    return successful_pings > 0

# DIRECT REPLACEMENT CODE for network_statistics_monitor.py
MONITOR_REPLACEMENT_CODE = '''
def _collect_latency_stats(self, timestamp):
    """REAL PINGS ONLY - No simulation fallback"""
    try:
        import requests
        import re
        
        real_measurements = 0
        print("📊 Collecting REAL latency measurements only...")
        
        for src, dst in self.latency_test_pairs:
            try:
                ping_command = f"{src} ping -c 1 -W 2 {dst}"
                response = requests.post('http://localhost:5000/api/execute', 
                                       json={'command': ping_command}, timeout=8)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        output = result.get('output', '')
                        if 'time=' in output:
                            time_match = re.search(r'time=([\d.]+)', output)
                            if time_match:
                                latency = float(time_match.group(1))
                                self.latency_stats[f"{src}-{dst}"].append({
                                    'timestamp': timestamp,
                                    'src': src,
                                    'dst': dst,
                                    'latency_ms': latency,
                                    'status': 'real_ping'
                                })
                                real_measurements += 1
                                print(f"📊 REAL {src}→{dst}: {latency:.2f}ms")
                
                time.sleep(0.2)  # Delay between pings
                
            except Exception as e:
                print(f"❌ Ping error {src}→{dst}: {e}")
                continue
        
        if real_measurements > 0:
            print(f"✅ Collected {real_measurements} REAL latency measurements")
        else:
            print("⚠️ No real latency measurements this cycle")
            
    except Exception as e:
        print(f"❌ Error in real latency collection: {e}")
'''

# DIRECT REPLACEMENT CODE for dashboard_utils.py
DASHBOARD_REPLACEMENT_CODE = '''
def get_real_time_latency_stats():
    """REAL PINGS ONLY - No simulation"""
    try:
        import requests
        import re
        
        test_pairs = [
            ('h1', 'h3'), ('h1', 'h5'), ('h1', 'h7'),
            ('h3', 'h5'), ('h3', 'h7'), ('h5', 'h7'),
            ('h2', 'h6'), ('h4', 'h8')
        ]
        
        latency_data = {}
        
        for src, dst in test_pairs:
            try:
                ping_command = f"{src} ping -c 1 -W 2 {dst}"
                response = requests.post('http://localhost:5000/api/execute', 
                                       json={'command': ping_command}, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        output = result.get('output', '')
                        if 'time=' in output:
                            time_match = re.search(r'time=([\d.]+)', output)
                            if time_match:
                                latency = float(time_match.group(1))
                                latency_data[f"{src}-{dst}"] = latency
                
                time.sleep(0.1)
                
            except:
                continue
        
        return latency_data
        
    except Exception as e:
        print(f"❌ Error getting real latency: {e}")
        return {}
'''

if __name__ == '__main__':
    print("🎯 REAL LATENCY MEASUREMENTS ONLY")
    print("=" * 35)
    print("This eliminates all simulation - only real ping results")
    print()
    
    # Test real pings
    if test_real_pings_only():
        print("\n🔧 APPLY THE FIX:")
        print()
        update_network_monitor_for_real_only()
        print()
        update_dashboard_utils_for_real_only()
        
        print("\n📋 OR COPY-PASTE THIS CODE:")
        print("\n1. In network_statistics_monitor.py, replace _collect_latency_stats:")
        print(MONITOR_REPLACEMENT_CODE)
        
        print("\n2. In dashboard_utils.py, replace get_real_time_latency_stats:")
        print(DASHBOARD_REPLACEMENT_CODE)
        
    else:
        print("\n❌ Real pings not working. Fix dashboard connection first.")
