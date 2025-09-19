#!/usr/bin/env python3
"""
auto_monitoring_integration.py
SAFE integration to automatically start monitoring and containers WITHOUT modifying your main code
Just import this file in your main_controller.py
"""

import time
import threading

def auto_start_monitoring_and_containers(controller):
    """
    Safely start monitoring and containers automatically
    This is called AFTER your controller is fully initialized
    """
    
    def delayed_startup():
        """Run startup in a separate thread to avoid blocking"""
        time.sleep(2)  # Wait for controller to be fully ready
        
        print("\n🚀 AUTO-STARTING Monitoring & Containers...")
        print("=" * 50)
        
        # 1. Start Statistics Monitoring
        try:
            if hasattr(controller, 'start_stats_monitoring'):
                result = controller.start_stats_monitoring()
                print(f"✅ Statistics monitoring: {result}")
            else:
                # Fallback: manually integrate stats monitoring
                from stats_integration import add_stats_monitoring_to_controller
                add_stats_monitoring_to_controller(controller)
                controller.start_stats_monitoring()
                print("✅ Statistics monitoring: Started (manual integration)")
        except Exception as e:
            print(f"⚠️ Statistics monitoring failed: {e}")
        
        # 2. Start Container Monitoring
        try:
            from container_stats_addon import ContainerStatsAddon
            controller.container_addon = ContainerStatsAddon('./network_stats')
            
            if controller.container_addon.start_containers():
                print("✅ Container monitoring: Alpine containers started")
            else:
                print("⚠️ Container monitoring: Failed to start containers")
        except Exception as e:
            print(f"⚠️ Container monitoring failed: {e}")
        
        print("🎉 AUTO-START Complete!")
        print("📊 Dashboard: http://localhost:5000")
        print("📈 Statistics: http://localhost:5000/stats")
        print("🐳 Container stats will appear in dashboard")
    
    # Start in background thread so it doesn't block your controller
    startup_thread = threading.Thread(target=delayed_startup, daemon=True)
    startup_thread.start()

def auto_cleanup_monitoring_and_containers(controller):
    """
    Safely cleanup all monitoring when controller exits
    """
    print("\n🧹 AUTO-CLEANUP Monitoring & Containers...")
    
    try:
        # Cleanup statistics monitoring
        if hasattr(controller, 'stats_monitor'):
            controller.stats_monitor.stop_monitoring()
            print("🛑 Statistics monitoring stopped")
    except Exception as e:
        print(f"⚠️ Stats cleanup warning: {e}")
    
    try:
        # Cleanup container monitoring
        if hasattr(controller, 'container_addon'):
            controller.container_addon.cleanup_all()
            print("🛑 Container monitoring cleaned up")
    except Exception as e:
        print(f"⚠️ Container cleanup warning: {e}")
    
    print("✅ AUTO-CLEANUP Complete!")
