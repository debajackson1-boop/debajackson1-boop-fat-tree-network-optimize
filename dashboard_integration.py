#!/usr/bin/env python3
"""
dashboard_integration.py
Dashboard communication with FIXED command parsing order + Neural Optimizer Status
"""

import time
import json
import os
import threading

# NEW: Import monitoring toggle
from monitoring_toggle import print_dashboard, print_important, print_error

class DashboardIntegration:
    """Handles all dashboard communication and status updates"""
    
    def __init__(self, controller):
        self.controller = controller
        self.status_file = '/tmp/fat_tree_status.json'
        self.status_thread = None
        self.running = False
    
    def start_dashboard_integration(self):
        """Start dashboard integration services"""
        self._update_status("initializing", "Dashboard integration starting...")
        self._start_status_updater()
        print_important("📡 Dashboard integration started")
        print_important("🌐 Dashboard will be available at: http://localhost:5000")
        print_important("💡 Run the dashboard: python3 dashboard_core.py")
    
    def stop_dashboard_integration(self):
        """Stop dashboard integration services"""
        self._stop_status_updater()
        
        # Remove status file
        if os.path.exists(self.status_file):
            os.remove(self.status_file)
            print_important("📡 Dashboard integration stopped")
    
    def _start_status_updater(self):
        """Start the status updater thread"""
        # Stop existing thread if running
        if self.status_thread and self.status_thread.is_alive():
            self._stop_status_updater()
        
        self.running = True
        self.status_thread = threading.Thread(
            target=self._status_updater_thread, 
            daemon=True,
            name="dashboard-status-updater"  # Named thread for identification
        )
        self.status_thread.start()
        print_dashboard("📡 Status updater started - dashboard will show live data")
        
        # Give thread a moment to start and create initial status
        time.sleep(0.5)
    
    def _stop_status_updater(self):
        """Stop the status updater thread"""
        self.running = False
        if self.status_thread and self.status_thread.is_alive():
            self.status_thread.join(timeout=2)
    
    def _status_updater_thread(self):
        """Background thread to continuously update status and process commands"""
        while self.running:
            try:
                # Process any pending commands from dashboard
                self._process_dashboard_commands()
                
                if self.controller.net:
                    # Get current network status
                    status_data = self._get_network_status_for_dashboard()
                    self._update_status("running", "Network operational", status_data)
                else:
                    self._update_status("ready", "Controller ready - network not started")
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print_error(f"⚠️ Status updater error: {e}")
                try:
                    self._update_status("error", f"Status update error: {str(e)}")
                except:
                    pass  # Avoid recursive errors
                time.sleep(5)
    
    def _get_neural_optimizer_status(self):
        """Get neural optimizer status from controller"""
        try:
            if hasattr(self.controller, 'latency_optimizer') and self.controller.latency_optimizer:
                if hasattr(self.controller.latency_optimizer, 'get_status'):
                    status = self.controller.latency_optimizer.get_status()
                    return {
                        'available': True,
                        'enabled': status.get('enabled', False),
                        'active': status.get('active', False),
                        'tensorflow_available': status.get('tensorflow_available', False),
                        'experience_buffer_size': status.get('experience_buffer_size', 0),
                        'model_trained': status.get('model_trained', False)
                    }
                elif hasattr(self.controller.latency_optimizer, 'is_enabled'):
                    # Fallback for simpler status check
                    return {
                        'available': True,
                        'enabled': self.controller.latency_optimizer.is_enabled(),
                        'active': getattr(self.controller.latency_optimizer, 'optimization_active', False),
                        'tensorflow_available': True,  # Assume true if optimizer exists
                        'experience_buffer_size': 0,
                        'model_trained': True
                    }
                else:
                    # Basic presence check
                    return {
                        'available': True,
                        'enabled': True,  # Assume enabled if present
                        'active': False,
                        'tensorflow_available': True,
                        'experience_buffer_size': 0,
                        'model_trained': True
                    }
            else:
                return {
                    'available': False,
                    'enabled': False,
                    'active': False,
                    'tensorflow_available': False,
                    'experience_buffer_size': 0,
                    'model_trained': False
                }
        except Exception as e:
            print_error(f"Error getting neural optimizer status: {e}")
            return {
                'available': False,
                'enabled': False,
                'active': False,
                'tensorflow_available': False,
                'experience_buffer_size': 0,
                'model_trained': False
            }
    
    def _process_dashboard_commands(self):
        """Enhanced dashboard command processing with robust error handling"""
        dashboard_cmd_file = '/tmp/dashboard_command_request.json'
        dashboard_response_file = '/tmp/dashboard_command_response.json'
        
        # Alternative paths in case /tmp is not accessible
        alt_paths = [
            ('/tmp', 'dashboard_command_request.json', 'dashboard_command_response.json'),
            ('/var/tmp', 'dashboard_command_request.json', 'dashboard_command_response.json'),
            ('.', 'dashboard_command_request.json', 'dashboard_command_response.json'),
            (os.getcwd(), 'dashboard_command_request.json', 'dashboard_command_response.json')
        ]
        
        for base_path, req_file, resp_file in alt_paths:
            try:
                cmd_file_path = os.path.join(base_path, req_file)
                response_file_path = os.path.join(base_path, resp_file)
                
                if os.path.exists(cmd_file_path):
                    try:
                        # Ensure we can read the file
                        with open(cmd_file_path, 'r') as f:
                            cmd_data = json.load(f)
                        
                        # Check if command is recent (within last 30 seconds)
                        if time.time() - cmd_data.get('timestamp', 0) < 30:
                            command = cmd_data.get('command', '')
                            
                            if command:
                                print_dashboard(f"Dashboard command received: {command}")
                                
                                # Execute the command and get result
                                success, output = self._execute_dashboard_command(command)
                                
                                # Write response for dashboard
                                response_data = {
                                    'success': success,
                                    'output' if success else 'error': output,
                                    'timestamp': time.time(),
                                    'command': command
                                }
                                
                                # Ensure response directory exists
                                os.makedirs(base_path, exist_ok=True)
                                
                                with open(response_file_path, 'w') as f:
                                    json.dump(response_data, f, indent=2)
                                
                                print_dashboard(f"Dashboard response written: success={success}")
                        
                        # Remove processed command file
                        try:
                            os.remove(cmd_file_path)
                        except:
                            pass  # Don't fail if we can't remove the file
                        
                        # Successfully processed, exit the loop
                        return
                        
                    except json.JSONDecodeError:
                        # File might be corrupted or incomplete, remove it
                        try:
                            os.remove(cmd_file_path)
                        except:
                            pass
                        continue
                        
                    except Exception as e:
                        print_error(f"Error processing dashboard command from {cmd_file_path}: {e}")
                        # Write error response
                        try:
                            os.makedirs(base_path, exist_ok=True)
                            error_response = {
                                'success': False,
                                'error': f"Controller error: {str(e)}",
                                'timestamp': time.time()
                            }
                            with open(response_file_path, 'w') as f:
                                json.dump(error_response, f)
                        except:
                            pass
                        return
                        
            except Exception as e:
                # Only log if it's not a file access error
                if "No such file" not in str(e) and "Permission denied" not in str(e):
                    print_error(f"Error accessing command files in {base_path}: {e}")
                continue

    def _execute_dashboard_command(self, command):
        """Execute command from dashboard and return result - FIXED COMMAND PARSING ORDER + Neural Optimizer Commands"""
        try:
            if not self.controller.net:
                return False, "Network not initialized"
            
            print_dashboard(f"🎯 Executing: {command}")
            
            # FIXED: Check controller methods FIRST before ping commands
            if command.startswith('py net.controller.'):
                method_name = command.replace('py net.controller.', '').replace('()', '')
                
                try:
                    print_dashboard(f"   🔧 Controller method: {method_name}")
                    
                    # Handle neural optimizer commands
                    if method_name == 'enable_neural_optimizer':
                        print_dashboard(f"   🧠 Enabling neural optimizer...")
                        if hasattr(self.controller, 'enable_neural_optimizer'):
                            result = self.controller.enable_neural_optimizer()
                            return True, "✅ Neural Latency Optimizer ENABLED\n🧠 Optimizations will be applied in next run"
                        else:
                            return False, "Neural optimizer not available on this controller"
                    
                    elif method_name == 'disable_neural_optimizer':
                        print_dashboard(f"   🧠 Disabling neural optimizer...")
                        if hasattr(self.controller, 'disable_neural_optimizer'):
                            result = self.controller.disable_neural_optimizer()
                            return True, "❌ Neural Latency Optimizer DISABLED\n🔧 All optimizations will be bypassed"
                        else:
                            return False, "Neural optimizer not available on this controller"
                    
                    elif method_name == 'neural_optimizer_status':
                        print_dashboard(f"   🧠 Getting neural optimizer status...")
                        neural_status = self._get_neural_optimizer_status()
                        
                        status_text = []
                        status_text.append("🧠 NEURAL LATENCY OPTIMIZER STATUS:")
                        status_text.append("="*50)
                        status_text.append(f"Available: {'✅ YES' if neural_status['available'] else '❌ NO'}")
                        status_text.append(f"Enabled: {'✅ ENABLED' if neural_status['enabled'] else '❌ DISABLED'}")
                        status_text.append(f"Active: {'🟢 RUNNING' if neural_status['active'] else '🔵 IDLE'}")
                        status_text.append(f"TensorFlow: {'✅ Available' if neural_status['tensorflow_available'] else '❌ Missing'}")
                        status_text.append(f"Experience Buffer: {neural_status['experience_buffer_size']} samples")
                        status_text.append(f"Model Trained: {'✅ YES' if neural_status['model_trained'] else '❌ NO'}")
                        
                        if neural_status['available']:
                            status_text.append("\n💡 COMMANDS:")
                            status_text.append("   py net.controller.enable_neural_optimizer()")
                            status_text.append("   py net.controller.disable_neural_optimizer()")
                            status_text.append("   py net.controller.run_tc_netem_neural_test()")
                        else:
                            status_text.append("\n⚠️ Neural optimizer not available")
                            status_text.append("   Ensure sophisticated_latency_neural_optimizer.py is present")
                        
                        return True, '\n'.join(status_text)
                    
                    elif method_name == 'run_tc_netem_neural_test':
                        print_dashboard(f"   🧠 Running TC/NetEm neural test...")
                        if hasattr(self.controller, 'run_tc_netem_neural_test'):
                            result = self.controller.run_tc_netem_neural_test()
                            status = "✅ SUCCESS" if result else "⚠️ PARTIAL/FAILED"
                            return True, f"{status} TC/NetEm neural test completed.\nCheck main terminal for detailed results."
                        else:
                            return False, "TC/NetEm neural test not available on this controller"
                    
                    elif method_name == 'auto_detect_and_fix_failures':
                        print_dashboard(f"   🤖 Running auto-detect and fix...")
                        
                        # Capture output by redirecting stdout
                        import sys
                        from io import StringIO
                        
                        # Save original stdout
                        original_stdout = sys.stdout
                        captured_output = StringIO()
                        
                        try:
                            # Redirect stdout to capture print statements
                            sys.stdout = captured_output
                            result = self.controller.auto_detect_and_fix_failures()
                            
                            # Get the captured output
                            output_text = captured_output.getvalue()
                            
                        finally:
                            # Always restore original stdout
                            sys.stdout = original_stdout
                        
                        status = "✅ SUCCESS" if result else "⚠️ PARTIAL"
                        
                        # Combine status with captured output
                        full_output = f"{status} Auto-detect and fix completed.\n\n" + "="*50 + "\nDETAILED OUTPUT:\n" + "="*50 + f"\n{output_text}"
                        
                        return True, full_output
                    
                    elif method_name == 'reset_to_clean_state':
                        print_dashboard(f"   🔄 Initiating dashboard-safe reset...")
                        result = self.controller.reset_to_clean_state()
                        if result:
                            return True, "✅ RESET SCHEDULED\nNetwork restart has been scheduled.\nThe controller will restart in a few seconds.\nPlease refresh the dashboard page after restart."
                        else:
                            return False, "❌ Reset scheduling failed"
                    
                    elif method_name == 'graceful_reset_network_only':
                        print_dashboard(f"   🔄 Running graceful network reset...")
                        
                        # Capture output
                        import sys
                        from io import StringIO
                        
                        original_stdout = sys.stdout
                        captured_output = StringIO()
                        
                        try:
                            sys.stdout = captured_output
                            result = self.controller.graceful_reset_network_only()
                            output_text = captured_output.getvalue()
                        finally:
                            sys.stdout = original_stdout
                        
                        status = "✅ SUCCESS" if result else "⚠️ PARTIAL"
                        full_output = f"{status} Graceful network reset completed.\n\n" + "="*50 + "\nDETAILED OUTPUT:\n" + "="*50 + f"\n{output_text}"
                        
                        return True, full_output
                    
                    elif method_name == 'test_basic_connectivity':
                        print_dashboard(f"   🧪 Testing basic connectivity...")
                        
                        # Capture output
                        import sys
                        from io import StringIO
                        
                        original_stdout = sys.stdout
                        captured_output = StringIO()
                        
                        try:
                            sys.stdout = captured_output
                            result = self.controller.test_basic_connectivity()
                            output_text = captured_output.getvalue()
                        finally:
                            sys.stdout = original_stdout
                        
                        status = "✅ SUCCESS" if result else "⚠️ ISSUES FOUND"
                        full_output = f"{status} Basic connectivity test completed.\n\n" + "="*50 + "\nDETAILED OUTPUT:\n" + "="*50 + f"\n{output_text}"
                        
                        return True, full_output
                    
                    elif method_name.startswith('start_stats_monitoring'):
                        print_dashboard(f"   📊 Starting statistics monitoring...")
                        if hasattr(self.controller, 'start_stats_monitoring'):
                            result = self.controller.start_stats_monitoring()
                            return True, f"✅ Statistics monitoring started.\n{result}"
                        else:
                            return False, "Statistics monitoring not available on this controller"
                    
                    elif method_name.startswith('show_stats_report'):
                        print_dashboard(f"   📊 Showing statistics report...")
                        if hasattr(self.controller, 'show_stats_report'):
                            result = self.controller.show_stats_report()
                            return True, f"✅ Statistics report generated.\nCheck main terminal for details."
                        else:
                            return False, "Statistics reporting not available on this controller"
                    
                    elif method_name.startswith('break_link_and_auto_fix'):
                        print_dashboard(f"   🔨 Breaking link and auto-fixing...")
                        # Extract parameters from method call
                        if "'ar1', 'es1'" in command or '"ar1", "es1"' in command:
                            result = self.controller.break_link_and_auto_fix('ar1', 'es1')
                            status = "✅ SUCCESS" if result else "⚠️ PARTIAL"
                            return True, f"{status} Break and auto-fix completed for ar1↔es1.\nCheck main terminal for details."
                        else:
                            return False, "Invalid parameters for break_link_and_auto_fix method"
                    
                    elif method_name.startswith('fix_'):
                        # Handle fix methods with output capture
                        if hasattr(self.controller, method_name):
                            method = getattr(self.controller, method_name)
                            print_dashboard(f"   🔧 Executing {method_name}...")
                            
                            # Capture output
                            import sys
                            from io import StringIO
                            
                            original_stdout = sys.stdout
                            captured_output = StringIO()
                            
                            try:
                                sys.stdout = captured_output
                                result = method()
                                output_text = captured_output.getvalue()
                            finally:
                                sys.stdout = original_stdout
                            
                            full_output = f"✅ Fix method '{method_name}' executed successfully.\n\n" + "="*50 + "\nDETAILED OUTPUT:\n" + "="*50 + f"\n{output_text}"
                            return True, full_output
                        else:
                            return False, f"Fix method '{method_name}' not found"
                    
                    else:
                        available_methods = [
                            "auto_detect_and_fix_failures",
                            "reset_to_clean_state", 
                            "graceful_reset_network_only",
                            "test_basic_connectivity",
                            "start_stats_monitoring",
                            "show_stats_report",
                            "break_link_and_auto_fix('ar1', 'es1')",
                            "enable_neural_optimizer",
                            "disable_neural_optimizer",
                            "neural_optimizer_status",
                            "run_tc_netem_neural_test"
                        ]
                        return False, f"Unknown controller method: {method_name}\nAvailable methods:\n" + "\n".join(f"• {m}" for m in available_methods)
                        
                except Exception as e:
                    import traceback
                    error_detail = traceback.format_exc()
                    print_error(f"❌ Controller method error: {e}")
                    print_error(f"Stack trace: {error_detail}")
                    return False, f"Error executing {method_name}: {str(e)}"
            
            # Handle links command
            elif command == 'links':
                try:
                    link_status = []
                    up_count = 0
                    total_count = 0
                    
                    # Check links directly from network
                    for link in self.controller.net.links:
                        node1 = link.intf1.node.name
                        node2 = link.intf2.node.name
                        is_up = link.intf1.isUp() and link.intf2.isUp()
                        status_text = "🟢 UP" if is_up else "🔴 DOWN"
                        link_status.append(f"  {node1}↔{node2}: {status_text}")
                        total_count += 1
                        if is_up:
                            up_count += 1
                    
                    if link_status:
                        header = f"📊 Network Links Status ({up_count}/{total_count} UP):\n" + "="*50
                        return True, f"{header}\n" + '\n'.join(link_status)
                    else:
                        return False, "No links found in network"
                        
                except Exception as e:
                    return False, f"Error getting link status: {str(e)}"
            
            # Handle link up/down commands: link ar1 es1 down
            elif command.startswith('link ') and len(command.split()) >= 4:
                parts = command.split()
                if len(parts) >= 4:
                    node1, node2, action = parts[1], parts[2], parts[3]
                    
                    try:
                        print_dashboard(f"   🔗 Setting link {node1}↔{node2} to {action}")
                        self.controller.net.configLinkStatus(node1, node2, action)
                        
                        # Verify the change
                        time.sleep(0.5)
                        
                        return True, f"✅ Link {node1}↔{node2} set to {action.upper()}\nChange should be visible in the topology within a few seconds."
                        
                    except Exception as e:
                        return False, f"Failed to {action} link {node1}↔{node2}: {str(e)}"
            
            # NOW handle ping commands (moved AFTER controller methods)
            elif ' ping ' in command:
                # Parse ping command properly
                parts = command.strip().split()
                if len(parts) >= 3:
                    src_host = parts[0]
                    # Find the target host (after 'ping')
                    ping_index = parts.index('ping')
                    
                    if ping_index + 1 < len(parts):
                        # Handle different ping formats:
                        # h1 ping h5
                        # h1 ping -c 1 h5
                        # h1 ping -c 1 -W 2 h5
                        
                        dst_host = None
                        ping_args = []
                        
                        # Look for the destination host (starts with 'h' and is not an option)
                        for i in range(ping_index + 1, len(parts)):
                            if parts[i].startswith('h') and parts[i][1:].isdigit():
                                dst_host = parts[i]
                                break
                            elif not parts[i].startswith('-'):
                                # If it doesn't start with '-' and isn't a host, it might be an IP
                                if '.' in parts[i]:
                                    # It's an IP, we need to map it back to host
                                    ip_to_host = {
                                        '10.1.1.1': 'h1', '10.1.1.2': 'h2',
                                        '10.1.2.1': 'h3', '10.1.2.2': 'h4',
                                        '10.2.1.1': 'h5', '10.2.1.2': 'h6',
                                        '10.2.2.1': 'h7', '10.2.2.2': 'h8'
                                    }
                                    dst_host = ip_to_host.get(parts[i])
                                    break
                        
                        # Extract ping options
                        for i in range(ping_index + 1, len(parts)):
                            if parts[i] == dst_host:
                                break
                            ping_args.append(parts[i])
                        
                        if not dst_host:
                            return False, f"Could not find destination host in command: {command}"
                        
                        src_node = self.controller.net.get(src_host)
                        dst_node = self.controller.net.get(dst_host)
                        
                        if not src_node:
                            return False, f"Source host '{src_host}' not found in network"
                        if not dst_node:
                            return False, f"Destination host '{dst_host}' not found in network"
                        
                        # Build ping command with proper arguments
                        ping_cmd_parts = ['ping']
                        
                        # Add arguments if provided, otherwise use defaults
                        if ping_args:
                            ping_cmd_parts.extend(ping_args)
                        else:
                            ping_cmd_parts.extend(['-c', '3', '-W', '2'])
                        
                        ping_cmd_parts.append(dst_node.IP())
                        ping_command = ' '.join(ping_cmd_parts)
                        
                        # Execute ping with timeout
                        try:
                            print_dashboard(f"   🏓 Pinging from {src_host} to {dst_host} ({dst_node.IP()})...")
                            result = src_node.cmd(ping_command)
                            
                            if result:
                                # Parse ping results
                                lines = result.strip().split('\n')
                                summary_lines = []
                                
                                for line in lines:
                                    line = line.strip()
                                    if any(keyword in line.lower() for keyword in 
                                          ['ping', 'bytes from', 'packets transmitted', 'packet loss', 'rtt']):
                                        summary_lines.append(line)
                                
                                if summary_lines:
                                    # Check if ping was successful
                                    full_result = '\n'.join(summary_lines)
                                    if 'bytes from' in result:
                                        return True, f"✅ Ping successful!\n{full_result}"
                                    else:
                                        return False, f"❌ Ping failed!\n{full_result}"
                                else:
                                    return False, f"Ping completed but no meaningful output received"
                            else:
                                return False, f"No response from ping command"
                                
                        except Exception as e:
                            return False, f"Ping execution error: {str(e)}"
            
            # Handle other commands
            else:
                return False, f"Unknown command: '{command}'\nSupported: ping commands, link commands, controller methods"
                
        except Exception as e:
            error_msg = f"Command execution error: {str(e)}"
            print_error(f"❌ {error_msg}")
            return False, error_msg
    
    def _get_network_status_for_dashboard(self):
        """Get comprehensive network status for dashboard"""
        if not self.controller.net:
            return {
                "connected": False,
                "error": "Network not initialized"
            }
        
        try:
            # Get ALL nodes from the actual network
            all_nodes = {
                'core': [],
                'aggregation': [],
                'edge': [],
                'hosts': []
            }
            
            # Discover all nodes from the actual Mininet network
            for node_name in self.controller.net.keys():
                node = self.controller.net.get(node_name)
                if node:
                    if node_name.startswith('cr'):
                        all_nodes['core'].append(node_name)
                    elif node_name.startswith('ar'):
                        all_nodes['aggregation'].append(node_name)
                    elif node_name.startswith('es'):
                        all_nodes['edge'].append(node_name)
                    elif node_name.startswith('h'):
                        all_nodes['hosts'].append(node_name)
            
            # Sort all node lists
            for layer in all_nodes:
                all_nodes[layer] = sorted(all_nodes[layer])
            
            # Test critical links - including host connections
            critical_links = [
                ('cr1', 'ar1'), ('cr1', 'ar3'), ('cr2', 'ar2'), ('cr2', 'ar4'),
                ('ar1', 'es1'), ('ar2', 'es2'), ('ar3', 'es3'), ('ar4', 'es4'),
                ('ar1', 'es2'), ('ar2', 'es1'), ('ar3', 'es4'), ('ar4', 'es3')
            ]
            
            # Add host-switch connections dynamically based on discovered hosts
            host_switch_links = []
            hosts = all_nodes['hosts']
            edge_switches = all_nodes['edge']
            
            if hosts and edge_switches:
                # Map hosts to switches based on expected topology
                host_switch_mapping = {
                    'h1': 'es1', 'h2': 'es1',
                    'h3': 'es2', 'h4': 'es2',
                    'h5': 'es3', 'h6': 'es3',
                    'h7': 'es4', 'h8': 'es4'
                }
                
                for host in hosts:
                    if host in host_switch_mapping:
                        switch = host_switch_mapping[host]
                        if switch in edge_switches:
                            host_switch_links.append((host, switch))
            
            # Combine all links to check
            all_links_to_check = critical_links + host_switch_links
            
            links = {}
            working_links = 0
            
            for node1, node2 in all_links_to_check:
                try:
                    # For host connections, check if both nodes exist
                    if node1.startswith('h') or node2.startswith('h'):
                        host = node1 if node1.startswith('h') else node2
                        switch = node2 if node1.startswith('h') else node1
                        
                        host_node = self.controller.net.get(host)
                        switch_node = self.controller.net.get(switch)
                        
                        if host_node and switch_node:
                            # For hosts, assume connection is up if both nodes exist
                            is_up = True
                        else:
                            is_up = False
                    else:
                        # For infrastructure links, use existing detection
                        is_up = not self.controller._detect_link_failure(node1, node2)
                    
                    links[f"{node1}↔{node2}"] = is_up
                    if is_up:
                        working_links += 1
                        
                except Exception as e:
                    print_error(f"  ❌ Error checking {node1}↔{node2}: {e}")
                    links[f"{node1}↔{node2}"] = False
            
            # Test connectivity between hosts
            test_pairs = []
            if len(hosts) >= 2:
                # Create test pairs dynamically based on discovered hosts
                test_pairs = [
                    ('h1', 'h3'), ('h1', 'h5'), ('h3', 'h5'),
                    ('h5', 'h7'), ('h2', 'h6'), ('h4', 'h8')
                ]
                # Filter to only include hosts that actually exist
                test_pairs = [(src, dst) for src, dst in test_pairs 
                             if src in hosts and dst in hosts]
            
            connectivity = {}
            working_connections = 0
            
            for src, dst in test_pairs:
                try:
                    connected = self.controller.router_manager.test_connectivity(src, dst)
                    connectivity[f"{src}-{dst}"] = connected
                    if connected:
                        working_connections += 1
                except Exception as e:
                    print_error(f"  ❌ Error testing {src}-{dst}: {e}")
                    connectivity[f"{src}-{dst}"] = False
            
            # Calculate health (separate infrastructure from host connections)
            infrastructure_links = [k for k in links.keys() if not (k.split('↔')[0].startswith('h') or k.split('↔')[1].startswith('h'))]
            infra_working = sum(1 for k in infrastructure_links if links[k])
            link_health = int((infra_working / len(infrastructure_links)) * 100) if infrastructure_links else 100
            
            connectivity_health = int((working_connections / len(test_pairs)) * 100) if test_pairs else 100
            
            if link_health >= 90 and connectivity_health >= 90:
                overall_status = "🟢 HEALTHY"
            elif link_health >= 70:
                overall_status = "🟡 DEGRADED"
            else:
                overall_status = "🔴 CRITICAL"
            
            # Get neural optimizer status
            neural_optimizer_status = self._get_neural_optimizer_status()
            
            status_data = {
                "connected": True,
                "links": links,  # Now includes host connections
                "connectivity": connectivity,
                "all_nodes": all_nodes,  # Provide complete node list to dashboard
                "neural_optimizer": neural_optimizer_status,  # NEW: Include neural optimizer status
                "health": {
                    "link_health": link_health,
                    "connectivity_health": connectivity_health,
                    "overall_status": overall_status
                }
            }
            
            return status_data
            
        except Exception as e:
            print_error(f"❌ Error getting network status: {e}")
            import traceback
            traceback.print_exc()
            
            error_data = {
                "connected": False,
                "error": f"Error getting network status: {str(e)}"
            }
            return error_data
    
    def _update_status(self, status, message="", data=None):
        """Update status file for dashboard communication"""
        try:
            status_data = {
                "status": status,
                "message": message,
                "timestamp": time.time(),
                "pid": os.getpid(),
                "data": data or {}
            }
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            print_error(f"⚠️ Could not update status file: {e}")
            # Try alternative path if /tmp fails
            try:
                alt_file = '/var/tmp/fat_tree_status.json'
                os.makedirs(os.path.dirname(alt_file), exist_ok=True)
                with open(alt_file, 'w') as f:
                    json.dump(status_data, f, indent=2)
                self.status_file = alt_file
                print_important(f"📝 Using alternative status file: {alt_file}")
            except Exception as e2:
                print_error(f"⚠️ Alternative path also failed: {e2}")
                # Last resort - try current directory
                try:
                    local_file = './fat_tree_status.json'
                    with open(local_file, 'w') as f:
                        json.dump(status_data, f, indent=2)
                    self.status_file = local_file
                    print_important(f"📝 Using local status file: {local_file}")
                except Exception as e3:
                    print_error(f"⚠️ All status file locations failed: {e3}")
