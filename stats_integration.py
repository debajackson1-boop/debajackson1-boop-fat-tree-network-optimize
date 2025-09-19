#!/usr/bin/env python3
"""
stats_integration.py
Simple integration to add statistics monitoring to your existing controller
WITHOUT modifying any existing code
"""

from network_statistics_monitor import NetworkStatsMonitor

def add_stats_monitoring_to_controller(controller):
    """Add statistics monitoring to your existing Fat-Tree controller"""
    
    print("📊 Adding statistics monitoring to controller...")
    
    # Create stats monitor
    controller.stats_monitor = NetworkStatsMonitor(monitor_interval=5)
    
    # Add convenience methods
    def start_stats_monitoring():
        """Start statistics collection"""
        controller.stats_monitor.start_monitoring()
        return "📊 Statistics monitoring started"
    
    def stop_stats_monitoring():
        """Stop statistics collection"""
        controller.stats_monitor.stop_monitoring()
        return "🛑 Statistics monitoring stopped"
    
    def show_stats_report():
        """Show current statistics report"""
        controller.stats_monitor.generate_report()
        return "📊 Statistics report displayed"
    
    def get_real_time_stats():
        """Get real-time statistics"""
        return controller.stats_monitor.get_real_time_stats()
    
    def show_traffic_stats():
        """Show current traffic statistics"""
        stats = controller.stats_monitor.get_real_time_stats()
        
        if 'traffic' in stats:
            print("\n📈 Current Traffic Statistics:")
            print("-" * 40)
            for switch, switch_stats in stats['traffic'].items():
                print(f"🔌 {switch}:")
                print(f"   Flows: {switch_stats['flow_count']}")
                print(f"   Packets: {switch_stats['total_packets']:,}")
                print(f"   Bytes: {switch_stats['total_bytes']:,}")
                print(f"   Avg Packet Size: {switch_stats['avg_packet_size']:.1f} bytes")
                print()
        else:
            print("📈 No traffic statistics available yet")
        
        return "📈 Traffic statistics displayed"
    
    def show_latency_stats():
        """Show current latency statistics"""
        stats = controller.stats_monitor.get_real_time_stats()
        
        if 'latency' in stats:
            print("\n⏱️ Current Latency Statistics:")
            print("-" * 40)
            for pair, latency in stats['latency'].items():
                status = "🟢" if latency < 10 else "🟡" if latency < 50 else "🔴"
                print(f"{status} {pair}: {latency:.2f} ms")
        else:
            print("⏱️ No latency statistics available yet")
        
        return "⏱️ Latency statistics displayed"
    
    def show_admission_and_latency():
        """Combined view of admission control and latency"""
        print("\n🔄 COMBINED NETWORK STATUS")
        print("=" * 40)
        
        # Show admission control status
        controller.show_admission_status()
        
        # Show latency stats
        stats = controller.stats_monitor.get_real_time_stats()
        if 'latency' in stats:
            print("\n⏱️ Network Latency:")
            for pair, latency in stats['latency'].items():
                if latency < 5:
                    status = "🟢 Excellent"
                elif latency < 20:
                    status = "🟡 Good"
                else:
                    status = "🔴 High"
                print(f"   {pair}: {latency:.2f}ms {status}")
        
        return "🔄 Combined status displayed"
    
    # Add methods to controller
    controller.start_stats_monitoring = start_stats_monitoring
    controller.stop_stats_monitoring = stop_stats_monitoring
    controller.show_stats_report = show_stats_report
    controller.get_real_time_stats = get_real_time_stats
    controller.show_traffic_stats = show_traffic_stats
    controller.show_latency_stats = show_latency_stats
    controller.show_admission_and_latency = show_admission_and_latency
    
    print("✅ Statistics monitoring integrated!")
    print("\n📋 NEW STATISTICS COMMANDS:")
    print("   py net.controller.start_stats_monitoring()")
    print("   py net.controller.show_stats_report()")
    print("   py net.controller.show_traffic_stats()")
    print("   py net.controller.show_latency_stats()")
    print("   py net.controller.show_admission_and_latency()")
    print("   py net.controller.stop_stats_monitoring()")
    print("\n📁 Statistics will be saved to: ./network_stats/")
    
    return controller.stats_monitor
