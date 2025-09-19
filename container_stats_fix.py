#!/usr/bin/env python3
"""
container_stats_fix.py
Fix the container statistics loading issue
"""

import subprocess
import time
import os

def check_docker():
    """Check if Docker is available and running"""
    print("🐳 Checking Docker...")
    
    try:
        result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker installed: {result.stdout.strip()}")
        else:
            print("❌ Docker not installed")
            return False
    except:
        print("❌ Docker not available")
        return False
    
    try:
        result = subprocess.run("docker ps", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker daemon running")
            return True
        else:
            print("❌ Docker daemon not running")
            return False
    except:
        print("❌ Cannot access Docker daemon")
        return False

def start_containers_manually():
    """Start Alpine containers manually"""
    print("\n🚀 Starting Alpine containers manually...")
    
    # Remove any existing containers
    print("   Cleaning up existing containers...")
    subprocess.run("docker rm -f alpine_h1 alpine_h3 2>/dev/null", shell=True)
    
    # Start containers
    print("   Starting alpine_h1...")
    result1 = subprocess.run("docker run -d --name alpine_h1 alpine:latest sleep 3600", 
                           shell=True, capture_output=True, text=True)
    
    print("   Starting alpine_h3...")
    result2 = subprocess.run("docker run -d --name alpine_h3 alpine:latest sleep 3600", 
                           shell=True, capture_output=True, text=True)
    
    if result1.returncode == 0 and result2.returncode == 0:
        print("✅ Containers started successfully")
        
        # Verify they're running
        time.sleep(2)
        result = subprocess.run("docker ps --filter name=alpine_", shell=True, capture_output=True, text=True)
        if "alpine_h1" in result.stdout and "alpine_h3" in result.stdout:
            print("✅ Both containers verified running")
            return True
        else:
            print("⚠️ Containers started but verification failed")
            return False
    else:
        print("❌ Failed to start containers")
        if result1.returncode != 0:
            print(f"   alpine_h1 error: {result1.stderr}")
        if result2.returncode != 0:
            print(f"   alpine_h3 error: {result2.stderr}")
        return False

def start_container_monitoring():
    """Start container monitoring manually"""
    print("\n📊 Starting container monitoring...")
    
    try:
        from container_stats_addon import ContainerStatsAddon
        
        # Create addon and start monitoring
        addon = ContainerStatsAddon('./network_stats')
        
        print("   Collecting container stats...")
        addon.collect_container_stats()
        
        # Check if files were created
        container_file = './network_stats/container_stats.csv'
        history_file = './network_logs/container_history.csv'
        
        if os.path.exists(container_file):
            with open(container_file, 'r') as f:
                lines = f.readlines()
                print(f"✅ Container stats file created: {len(lines)} lines")
        else:
            print("❌ Container stats file not created")
            
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                lines = f.readlines()
                print(f"✅ Container history file created: {len(lines)} lines")
        else:
            print("❌ Container history file not created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting monitoring: {e}")
        return False

def test_dashboard_api():
    """Test the dashboard container API"""
    print("\n🌐 Testing dashboard API...")
    
    import requests
    import json
    
    try:
        # Test container stats API
        response = requests.get('http://localhost:5000/api/stats/containers', timeout=5)
        data = response.json()
        
        print(f"📡 Container API response: {data}")
        
        if data.get('success'):
            print("✅ Container API working")
            if data.get('data'):
                print(f"   Container data: {data['data']}")
            else:
                print("   No container data available yet")
        else:
            print(f"❌ Container API error: {data.get('error')}")
            
        # Test container summary API
        response = requests.get('http://localhost:5000/api/stats/container_summary', timeout=5)
        data = response.json()
        
        if data.get('success'):
            print("✅ Container summary API working")
            if data.get('data'):
                print(f"   Summary data: {data['data']}")
        else:
            print(f"❌ Container summary API error: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

def fix_container_stats():
    """Complete fix for container statistics"""
    print("🔧 Container Statistics Fix")
    print("=" * 30)
    
    # Step 1: Check Docker
    if not check_docker():
        print("\n❌ Docker is required for container statistics")
        print("Please install Docker and try again")
        return False
    
    # Step 2: Start containers
    if not start_containers_manually():
        print("\n❌ Failed to start containers")
        return False
    
    # Step 3: Start monitoring
    if not start_container_monitoring():
        print("\n❌ Failed to start monitoring")
        return False
    
    # Step 4: Test API
    test_dashboard_api()
    
    print("\n🎉 Container statistics should now be working!")
    print("📊 Refresh your dashboard: http://localhost:5000/stats")
    print("⏱️ Wait 10-15 seconds for data to appear")
    
    return True

if __name__ == '__main__':
    fix_container_stats()
