#!/usr/bin/env python3
"""
container_fix.py
Complete container statistics fix with proper memory parsing
This file provides fixed container API routes that can be imported into dashboard_core.py
"""

import os
import csv
import subprocess
import re
from flask import jsonify

def parse_memory_value_fixed(memory_str):
    """Parse memory values like '2.93k', '3.68k' properly - FIXED VERSION"""
    if not memory_str or memory_str == '0' or memory_str == '':
        return 0.0
    
    memory_str = str(memory_str).strip()
    
    # Handle plain numbers first (assume MB)
    try:
        return float(memory_str)
    except:
        pass
    
    # Handle units with regex - FIXED PARSING
    match = re.match(r'([0-9.]+)([kmgtKMGT]?)', memory_str.lower())
    if match:
        value_str, unit = match.groups()
        try:
            value = float(value_str)
            
            # FIX: Correct unit conversions
            if unit.lower() == 'k':
                return value / 1024  # KB to MB: DIVIDE by 1024
            elif unit.lower() == 'm' or unit == '':
                return value  # Already MB or assume MB
            elif unit.lower() == 'g':
                return value * 1024  # GB to MB
            elif unit.lower() == 't':
                return value * 1024 * 1024  # TB to MB
            else:
                return value  # Unknown unit, return as-is
        except ValueError:
            print(f"Warning: Could not parse numeric part: '{value_str}' from '{memory_str}'")
            return 0.0
    
    print(f"Warning: Could not parse memory value: '{memory_str}'")
    return 0.0

def parse_cpu_percent_fixed(cpu_str):
    """Parse CPU percentage values - IMPROVED VERSION"""
    if not cpu_str or cpu_str == '0' or cpu_str == '':
        return 0.0
    
    try:
        # Remove % symbol and any whitespace
        cpu_str = str(cpu_str).replace('%', '').strip()
        return float(cpu_str)
    except ValueError:
        print(f"Warning: Could not parse CPU value: '{cpu_str}'")
        return 0.0

def get_running_containers():
    """Get list of running Alpine containers"""
    running_containers = {}
    try:
        result = subprocess.run("docker ps --filter name=alpine_ --format '{{.Names}}'", 
                               shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if 'alpine_h1' in line:
                    running_containers['h1'] = {'status': 'running', 'container': 'alpine_h1'}
                elif 'alpine_h3' in line:
                    running_containers['h3'] = {'status': 'running', 'container': 'alpine_h3'}
    except Exception as e:
        print(f"Warning: Could not check running containers: {e}")
    
    return running_containers

def read_container_stats_from_csv():
    """Read container stats from CSV file with FIXED parsing"""
    container_file = './network_stats/container_stats.csv'
    
    if not os.path.exists(container_file):
        return None
    
    try:
        container_data = {}
        
        with open(container_file, 'r') as f:
            lines = f.readlines()
            
            if len(lines) <= 1:  # Only header or empty
                return None
            
            # Process lines in reverse order to get latest data for each host
            for line in reversed(lines[1:]):  # Skip header
                try:
                    data = line.strip().split(',')
                    if len(data) < 8:  # Not enough columns
                        continue
                    
                    host = data[1].strip()
                    if host in ['h1', 'h3'] and host not in container_data:
                        # Parse with FIXED functions
                        cpu_val = parse_cpu_percent_fixed(data[4])
                        mem_val = parse_memory_value_fixed(data[5])
                        
                        container_data[host] = {
                            'host': host,
                            'container': data[2].strip(),
                            'status': data[3].strip(),
                            'cpu_percent': cpu_val,
                            'memory_mb': mem_val,
                        }
                        
                        print(f"✅ Parsed {host}: CPU={cpu_val:.1f}%, MEM={mem_val:.3f}MB (from '{data[4].strip()}'->'{data[5].strip()}')")
                        
                except Exception as e:
                    print(f"⚠️ Parse error for line '{line.strip()}': {e}")
                    continue
        
        return container_data if container_data else None
        
    except Exception as e:
        print(f"❌ Error reading container stats file: {e}")
        return None

def read_container_history_summary():
    """Read container history summary with FIXED parsing"""
    history_file = './network_logs/container_history.csv'
    
    if not os.path.exists(history_file):
        return None, None
    
    try:
        with open(history_file, 'r') as f:
            lines = f.readlines()
            
            if len(lines) <= 1:  # Only header or empty
                return None, None
            
            # Get the latest line
            latest = lines[-1].strip().split(',')
            if len(latest) >= 5:
                avg_cpu = parse_cpu_percent_fixed(latest[3])
                total_mem = parse_memory_value_fixed(latest[4])
                print(f"✅ History summary: CPU={avg_cpu:.1f}%, MEM={total_mem:.3f}MB")
                return avg_cpu, total_mem
                
    except Exception as e:
        print(f"⚠️ Error reading container history: {e}")
    
    return None, None

def create_fixed_container_api_routes(app):
    """Create fixed container API routes - call this from dashboard_core.py"""
    
    @app.route('/api/stats/containers')
    def fixed_container_stats():
        """FIXED container stats API with proper memory parsing"""
        try:
            print("🔍 Getting container stats...")
            
            # Get running containers first
            running_containers = get_running_containers()
            
            # Try to get stats from CSV file with FIXED parsing
            container_data = read_container_stats_from_csv()
            
            if container_data:
                print(f"✅ Successfully parsed {len(container_data)} containers from CSV")
                return jsonify({'success': True, 'data': container_data})
            
            # Fallback to running containers without stats
            if running_containers:
                print("⚠️ No CSV stats available, using running container info only")
                for host in running_containers:
                    running_containers[host].update({
                        'cpu_percent': 0.0, 
                        'memory_mb': 0.0, 
                        'host': host
                    })
                return jsonify({'success': True, 'data': running_containers})
            
            # No containers found
            print("❌ No container data available")
            return jsonify({
                'success': False, 
                'error': 'No container data available. Start containers with: docker run -d --name alpine_h1 alpine:latest sleep 3600'
            })
            
        except Exception as e:
            print(f"❌ Container API error: {e}")
            return jsonify({'success': False, 'error': f'Container API error: {str(e)}'})

    @app.route('/api/stats/container_summary')
    def fixed_container_summary():
        """FIXED container summary API with proper parsing"""
        try:
            print("🔍 Getting container summary...")
            
            # Count running containers
            running_containers = get_running_containers()
            running_count = len(running_containers)
            h1_status = 'running' if 'h1' in running_containers else 'stopped'
            h3_status = 'running' if 'h3' in running_containers else 'stopped'
            
            # Get stats from history file with FIXED parsing
            avg_cpu, total_mem = read_container_history_summary()
            
            if avg_cpu is None:
                avg_cpu = 0.0
            if total_mem is None:
                total_mem = 0.0
            
            summary_data = {
                'total_containers': 2,
                'running_containers': running_count,
                'avg_cpu_percent': avg_cpu,
                'total_memory_mb': total_mem,
                'h1_status': h1_status,
                'h3_status': h3_status,
            }
            
            print(f"✅ Container summary: {running_count}/2 running, CPU={avg_cpu:.1f}%, MEM={total_mem:.1f}MB")
            return jsonify({'success': True, 'data': summary_data})
            
        except Exception as e:
            print(f"❌ Container summary error: {e}")
            return jsonify({'success': False, 'error': f'Container summary error: {str(e)}'})

    print("✅ Fixed container API routes added to Flask app")

def test_memory_parsing():
    """Test the fixed memory parsing function"""
    print("\n🧪 Testing FIXED memory parsing:")
    print("=" * 40)
    
    test_cases = [
        '2.93k',    # Should be ~2.86 MB
        '3.68k',    # Should be ~3.59 MB
        '1.5M',     # Should be 1.5 MB
        '512',      # Should be 512 MB
        '1.2G',     # Should be 1228.8 MB
        '0',        # Should be 0 MB
        '',         # Should be 0 MB
        'invalid',  # Should be 0 MB with warning
    ]
    
    for test_val in test_cases:
        result = parse_memory_value_fixed(test_val)
        if test_val == '2.93k':
            expected = "~2.86"
        elif test_val == '3.68k':
            expected = "~3.59"
        else:
            expected = "see above"
        print(f"  '{test_val:>8}' → {result:>8.3f} MB  (expected {expected})")
    
    print("\n🧪 Testing CPU parsing:")
    cpu_cases = ['45.2%', '0.5', '100', '', 'invalid']
    for test_val in cpu_cases:
        result = parse_cpu_percent_fixed(test_val)
        print(f"  '{test_val:>8}' → {result:>6.1f}%")
    
    print("=" * 40)
    print("✅ All parsing tests completed!")

if __name__ == '__main__':
    print("🔧 Container Stats Fix - Testing Parsing Functions")
    test_memory_parsing()
    
    print(f"\n💡 To use this fix:")
    print(f"   1. Import in dashboard_core.py:")
    print(f"      from container_fix import create_fixed_container_api_routes")
    print(f"   2. Add routes to Flask app:")
    print(f"      create_fixed_container_api_routes(app)")
    print(f"   3. Restart dashboard: python3 dashboard_core.py")
