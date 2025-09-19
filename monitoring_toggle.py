#!/usr/bin/env python3
"""
monitoring_toggle.py
Add verbose monitoring toggle to your controller
"""

import threading
import time

class MonitoringToggle:
    """Simple toggle system for monitoring messages"""
    
    def __init__(self):
        self.verbose_monitoring = False  # Default: quiet mode
        self.lock = threading.Lock()
    
    def enable_verbose(self):
        """Enable verbose monitoring messages"""
        with self.lock:
            self.verbose_monitoring = True
            print("🔊 Verbose monitoring messages ENABLED")
    
    def disable_verbose(self):
        """Disable verbose monitoring messages"""
        with self.lock:
            self.verbose_monitoring = False
            print("🔇 Verbose monitoring messages DISABLED")
    
    def toggle_verbose(self):
        """Toggle verbose monitoring on/off"""
        with self.lock:
            self.verbose_monitoring = not self.verbose_monitoring
            status = "ENABLED" if self.verbose_monitoring else "DISABLED"
            icon = "🔊" if self.verbose_monitoring else "🔇"
            print(f"{icon} Verbose monitoring messages {status}")
    
    def is_verbose(self):
        """Check if verbose mode is enabled"""
        with self.lock:
            return self.verbose_monitoring
    
    def print_if_verbose(self, message):
        """Print message only if verbose mode is enabled"""
        if self.is_verbose():
            print(message)

# Global toggle instance
monitoring_toggle = MonitoringToggle()

def add_toggle_commands_to_controller(controller):
    """Add toggle commands to your controller"""
    
    def enable_verbose_monitoring():
        """Enable verbose monitoring messages"""
        monitoring_toggle.enable_verbose()
        return "🔊 Verbose monitoring enabled - you'll see all ping and container messages"
    
    def disable_verbose_monitoring():
        """Disable verbose monitoring messages"""
        monitoring_toggle.disable_verbose()
        return "🔇 Verbose monitoring disabled - quiet mode active"
    
    def toggle_verbose_monitoring():
        """Toggle verbose monitoring on/off"""
        monitoring_toggle.toggle_verbose()
        status = "enabled" if monitoring_toggle.is_verbose() else "disabled"
        return f"🔄 Verbose monitoring {status}"
    
    def show_monitoring_status():
        """Show current monitoring status"""
        status = "ENABLED 🔊" if monitoring_toggle.is_verbose() else "DISABLED 🔇"
        return f"📊 Verbose monitoring: {status}"
    
    # Add methods to controller
    controller.enable_verbose_monitoring = enable_verbose_monitoring
    controller.disable_verbose_monitoring = disable_verbose_monitoring
    controller.toggle_verbose_monitoring = toggle_verbose_monitoring
    controller.show_monitoring_status = show_monitoring_status
    
    print("🎛️ Monitoring toggle commands added:")
    print("   py net.controller.enable_verbose_monitoring()")
    print("   py net.controller.disable_verbose_monitoring()")
    print("   py net.controller.toggle_verbose_monitoring()")
    print("   py net.controller.show_monitoring_status()")

# Functions to replace existing print statements

def print_monitoring(message):
    """Print monitoring message only if verbose is enabled"""
    monitoring_toggle.print_if_verbose(message)

def print_container(message):
    """Print container message only if verbose is enabled"""
    monitoring_toggle.print_if_verbose(message)

def print_ping(message):
    """Print ping message only if verbose is enabled"""
    monitoring_toggle.print_if_verbose(message)

def print_stats(message):
    """Print stats message only if verbose is enabled"""
    monitoring_toggle.print_if_verbose(message)

def print_dashboard(message):
    """Print dashboard message only if verbose is enabled"""
    monitoring_toggle.print_if_verbose(message)

# Always print these (important messages)
def print_important(message):
    """Always print important messages regardless of toggle"""
    print(message)

def print_error(message):
    """Always print error messages"""
    print(message)

def print_startup(message):
    """Always print startup messages"""
    print(message)
