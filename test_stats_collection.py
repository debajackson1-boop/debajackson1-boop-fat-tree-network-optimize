#!/usr/bin/env python3
"""
test_stats_collection.py
Quick test script to generate network activity and test statistics collection
"""

import time
import requests
import json

def send_command_to_dashboard(command):
    """Send command to dashboard API"""
    try:
        response = requests.post('http://localhost:5000/api/execute', 
                               json={'command': command}, 
                               timeout=10)
        result = response.json()
        return result.get('success', False), result.get('output', result.get('error', 'No response'))
    except Exception as e:
        return False, str(e)

def test_statistics_collection():
    """Test statistics collection by generating network activity"""
    print("🧪 Testing Statistics Collection")
    print("=" * 40)
    
    # Test commands to generate network activity
    test_commands = [
        'h1 ping -c 3 h3',
        'h1 ping -c 3 h5', 
        'h3 ping -c 3 h7',
        'h5 ping -c 3 h1',
        'h2 ping -c 2 h6',
        'h4 ping -c 2 h8'
    ]
    
    print("📊 Generating network activity...")
    
    for i, command in enumerate(test_commands, 1):
        print(f"   {i}. Executing: {command}")
        success, output = send_command_to_dashboard(command)
        
        if success:
            # Extract latency from ping output
            if 'time=' in output:
                import re
                times = re.findall(r'time=([\d.]+)', output)
                if times:
                    avg_latency = sum(float(t) for t in times) / len(times)
                    print(f"      ✅ Success! Average latency: {avg_latency:.2f}ms")
                else:
                    print(f"      ✅ Success! (no latency extracted)")
            else:
                print(f"      ✅ Success!")
        else:
            print(f"      ❌ Failed: {output}")
        
        time.sleep(1)  # Small delay between commands
    
    print(f"\n🔄 Waiting 3 seconds for statistics to update...")
    time.sleep(3)
    
    # Test statistics API endpoints
    print(f"\n📈 Testing Statistics API Endpoints...")
    
    endpoints = [
        ('Traffic Stats', 'http://localhost:5000/api/stats/traffic'),
        ('Latency Stats', 'http://localhost:5000/api/stats/latency'),
        ('Health Stats', 'http://localhost:5000/api/stats/health')
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('success'):
                print(f"   ✅ {name}: Working")
                if name == 'Traffic Stats' and 'data' in data:
                    # Show traffic summary
                    traffic_data = data['data']
                    total_packets = sum(switch.get('total_packets', 0) for switch in traffic_data.values())
                    print(f"      📊 Total packets across all switches: {total_packets}")
                elif name == 'Latency Stats' and 'data' in data:
                    # Show latency summary
                    latency_data = data['data']
                    if latency_data:
                        avg_latency = sum(latency_data.values()) / len(latency_data)
                        print(f"      ⏱️ Average latency: {avg_latency:.2f}ms")
                    else:
                        print(f"      ⏱️ No latency data available")
                elif name == 'Health Stats' and 'data' in data:
                    # Show health summary
                    health_data = data['data']
                    print(f"      🛡️ Link health: {health_data.get('link_health', 0)}%")
            else:
                print(f"   ❌ {name}: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ {name}: Connection error - {e}")
    
    print(f"\n🌐 Statistics Dashboard:")
    print(f"   Main: http://localhost:5000")
    print(f"   Stats: http://localhost:5000/stats")
    print(f"\n💡 You should now see updated statistics in the dashboard!")

def start_controller_stats_monitoring():
    """Start statistics monitoring on the controller"""
    print("🚀 Starting Controller Statistics Monitoring...")
    
    success, output = send_command_to_dashboard('py net.controller.start_stats_monitoring()')
    
    if success:
        print("✅ Statistics monitoring started on controller")
        print(f"📄 Output: {output}")
    else:
        print(f"❌ Failed to start monitoring: {output}")
    
    return success

def main():
    """Main test function"""
    print("🧪 Fat-Tree Statistics Collection Test")
    print("=" * 45)
    print("This script will:")
    print("1. Try to start statistics monitoring on controller")  
    print("2. Generate network activity with ping commands")
    print("3. Test all statistics API endpoints")
    print("4. Show you where to view the results")
    print()
    
    input("Press Enter to continue...")
    
    # Step 1: Start monitoring
    monitoring_started = start_controller_stats_monitoring()
    if monitoring_started:
        print("✅ Controller monitoring is active")
    else:
        print("⚠️ Controller monitoring failed - but dashboard stats should still work")
    
    print()
    
    # Step 2: Generate activity and test
    test_statistics_collection()
    
    print(f"\n🎉 Test Complete!")
    print(f"📊 Check your statistics dashboard at: http://localhost:5000/stats")

if __name__ == '__main__':
    main()
