#!/usr/bin/env python3
"""
fat_tree_autofix.py
All autofix methods for the Fat-Tree controller - FIXED AR2 failure
"""

import time

def fix_ar1_complete_failure(controller):
    """Fix complete AR1 router failure"""
    print("🔧 Fixing complete AR1 failure...")
    
    try:
        controller.net.configLinkStatus('ar1', 'cr1', 'down')
        controller.net.configLinkStatus('ar1', 'es1', 'down')
        controller.net.configLinkStatus('ar1', 'es2', 'down')
    except:
        pass
    
    h1 = controller.net.get('h1')
    h1.cmd('ip route del default 2>/dev/null || true')
    h1.cmd('ip route add default via 10.1.1.253')
    h1.cmd('ip route add 10.1.2.0/24 via 10.1.1.253 metric 1')
    h1.cmd('ip route add 10.2.0.0/16 via 10.1.1.253 metric 1')
    
    h2 = controller.net.get('h2')
    h2.cmd('ip route del default 2>/dev/null || true')
    h2.cmd('ip route add default via 10.1.1.253')
    h2.cmd('ip route add 10.1.2.0/24 via 10.1.1.253 metric 1')
    h2.cmd('ip route add 10.2.0.0/16 via 10.1.1.253 metric 1')
    
    h3 = controller.net.get('h3')
    h3.cmd('ip route del default 2>/dev/null || true')
    h3.cmd('ip route add default via 10.1.2.254')
    h3.cmd('ip route add 10.1.1.0/24 via 10.1.2.254 metric 1')
    h3.cmd('ip route add 10.2.0.0/16 via 10.1.2.254 metric 1')
    
    h4 = controller.net.get('h4')
    h4.cmd('ip route del default 2>/dev/null || true')
    h4.cmd('ip route add default via 10.1.2.254')
    h4.cmd('ip route add 10.1.1.0/24 via 10.1.2.254 metric 1')
    h4.cmd('ip route add 10.2.0.0/16 via 10.1.2.254 metric 1')
    
    ar2 = controller.net.get('ar2')
    ar2.cmd('ip route del 10.1.1.0/24 2>/dev/null || true')
    ar2.cmd('ip route add 10.1.1.0/24 dev ar2-eth3 metric 1')
    ar2.cmd('ip route add 10.2.1.0/24 via 172.16.6.1 metric 1')
    ar2.cmd('ip route add 10.2.2.0/24 via 172.16.6.1 metric 1')
    
    cr2 = controller.net.get('cr2')
    cr2.cmd('ip route add 10.1.1.0/24 via 172.16.6.2 metric 1')
    
    ar4 = controller.net.get('ar4')
    ar4.cmd('ip route del 10.2.1.0/24 2>/dev/null || true')
    ar4.cmd('ip route add 10.2.1.0/24 dev ar4-eth3 src 10.2.1.253 metric 1')
    
    ar3 = controller.net.get('ar3')
    ar3.cmd('ip route del 10.1.1.0/24 2>/dev/null || true')
    ar3.cmd('ip route add 10.1.1.0/24 via 10.2.1.253 metric 1')
    ar3.cmd('ip route del 10.1.2.0/24 2>/dev/null || true')
    ar3.cmd('ip route add 10.1.2.0/24 via 10.2.1.253 metric 1')
    
    print("✅ AR1 failure recovery complete")

def fix_ar2_complete_failure(controller):
    """Fix complete AR2 router failure - FIXED VERSION"""
    print("🔧 Fixing complete AR2 failure...")
    
    try:
        controller.net.configLinkStatus('ar2', 'cr2', 'down')
        controller.net.configLinkStatus('ar2', 'es2', 'down')
        controller.net.configLinkStatus('ar2', 'es1', 'down')
    except:
        pass
    
    # Fix hosts h3, h4 to use ar1's diagonal connection
    h3 = controller.net.get('h3')
    h3.cmd('ip route del default 2>/dev/null || true')
    h3.cmd('ip route add default via 10.1.2.253')  # ar1's IP on es2
    h3.cmd('ip route add 10.1.1.0/24 via 10.1.2.253 metric 1')
    h3.cmd('ip route add 10.2.0.0/16 via 10.1.2.253 metric 1')
    
    h4 = controller.net.get('h4')
    h4.cmd('ip route del default 2>/dev/null || true')
    h4.cmd('ip route add default via 10.1.2.253')  # ar1's IP on es2
    h4.cmd('ip route add 10.1.1.0/24 via 10.1.2.253 metric 1')
    h4.cmd('ip route add 10.2.0.0/16 via 10.1.2.253 metric 1')
    
    # Fix ar1 to handle es2 fully via diagonal connection
    ar1 = controller.net.get('ar1')
    ar1.cmd('ip route del 10.1.2.0/24 2>/dev/null || true')
    ar1.cmd('ip route add 10.1.2.0/24 dev ar1-eth3 metric 1')
    ar1.cmd('ip route del 10.2.0.0/16 2>/dev/null || true')
    ar1.cmd('ip route add 10.2.0.0/16 via 172.16.1.1 metric 1')  # via cr1
    
    # Fix cr1 to route pod2 via ar3
    cr1 = controller.net.get('cr1')
    cr1.cmd('ip route del 10.2.1.0/24 2>/dev/null || true')
    cr1.cmd('ip route del 10.2.2.0/24 2>/dev/null || true')
    cr1.cmd('ip route add 10.2.1.0/24 via 172.16.3.2 metric 1')  # via ar3
    cr1.cmd('ip route add 10.2.2.0/24 via 172.16.3.2 metric 1')  # via ar3
    
    # Fix ar3 to route pod1 via cr1
    ar3 = controller.net.get('ar3')
    ar3.cmd('ip route del 10.1.1.0/24 2>/dev/null || true')
    ar3.cmd('ip route del 10.1.2.0/24 2>/dev/null || true')
    ar3.cmd('ip route add 10.1.1.0/24 via 172.16.3.1 metric 1')  # via cr1
    ar3.cmd('ip route add 10.1.2.0/24 via 172.16.3.1 metric 1')  # via cr1
    
    # CRITICAL FIX: ar4 must route pod1 traffic via ar3 (not cr2)
    ar4 = controller.net.get('ar4')
    ar4.cmd('ip route del 10.1.1.0/24 2>/dev/null || true')
    ar4.cmd('ip route del 10.1.2.0/24 2>/dev/null || true')
    ar4.cmd('ip route add 10.1.1.0/24 via 10.2.1.254 metric 1')  # via ar3 on pod2 subnet
    ar4.cmd('ip route add 10.1.2.0/24 via 10.2.1.254 metric 1')  # via ar3 on pod2 subnet
    
    print("✅ AR2 failure recovery complete")

def fix_ar3_complete_failure(controller):
    """Fix complete AR3 router failure"""
    print("🔧 Fixing complete AR3 failure...")
    
    try:
        controller.net.configLinkStatus('ar3', 'cr1', 'down')
        controller.net.configLinkStatus('ar3', 'es3', 'down')
        controller.net.configLinkStatus('ar3', 'es4', 'down')
    except:
        pass
    
    h5 = controller.net.get('h5')
    h5.cmd('ip route del default 2>/dev/null || true')
    h5.cmd('ip route add default via 10.2.1.253')
    h5.cmd('ip route add 10.2.2.0/24 via 10.2.1.253 metric 1')
    h5.cmd('ip route add 10.1.0.0/16 via 10.2.1.253 metric 1')
    
    h6 = controller.net.get('h6')
    h6.cmd('ip route del default 2>/dev/null || true')
    h6.cmd('ip route add default via 10.2.1.253')
    h6.cmd('ip route add 10.2.2.0/24 via 10.2.1.253 metric 1')
    h6.cmd('ip route add 10.1.0.0/16 via 10.2.1.253 metric 1')
    
    h7 = controller.net.get('h7')
    h7.cmd('ip route del default 2>/dev/null || true')
    h7.cmd('ip route add default via 10.2.2.254')
    h7.cmd('ip route add 10.2.1.0/24 via 10.2.2.254 metric 1')
    h7.cmd('ip route add 10.1.0.0/16 via 10.2.2.254 metric 1')
    
    h8 = controller.net.get('h8')
    h8.cmd('ip route del default 2>/dev/null || true')
    h8.cmd('ip route add default via 10.2.2.254')
    h8.cmd('ip route add 10.2.1.0/24 via 10.2.2.254 metric 1')
    h8.cmd('ip route add 10.1.0.0/16 via 10.2.2.254 metric 1')
    
    ar4 = controller.net.get('ar4')
    ar4.cmd('ip route del 10.2.1.0/24 2>/dev/null || true')
    ar4.cmd('ip route add 10.2.1.0/24 dev ar4-eth3 src 10.2.1.253 metric 1')
    ar4.cmd('ip route add 10.1.1.0/24 via 172.16.8.1 metric 1')
    ar4.cmd('ip route add 10.1.2.0/24 via 172.16.8.1 metric 1')
    
    cr2 = controller.net.get('cr2')
    cr2.cmd('ip route add 10.2.1.0/24 via 172.16.8.2 metric 1')
    
    ar1 = controller.net.get('ar1')
    ar1.cmd('ip route del 10.2.1.0/24 2>/dev/null || true')
    ar1.cmd('ip route add 10.2.1.0/24 via 10.1.1.253 metric 1')
    ar1.cmd('ip route del 10.2.2.0/24 2>/dev/null || true')
    ar1.cmd('ip route add 10.2.2.0/24 via 10.1.1.253 metric 1')
    
    ar2 = controller.net.get('ar2')
    ar2.cmd('ip route del 10.2.1.0/24 2>/dev/null || true')
    ar2.cmd('ip route add 10.2.1.0/24 via 172.16.6.1 metric 1')
    ar2.cmd('ip route del 10.2.2.0/24 2>/dev/null || true')
    ar2.cmd('ip route add 10.2.2.0/24 via 172.16.6.1 metric 1')
    
    print("✅ AR3 failure recovery complete")

def fix_ar4_complete_failure(controller):
    """Fix complete AR4 router failure"""
    print("🔧 Fixing complete AR4 failure...")
    
    try:
        controller.net.configLinkStatus('ar4', 'cr2', 'down')
        controller.net.configLinkStatus('ar4', 'es4', 'down')
        controller.net.configLinkStatus('ar4', 'es3', 'down')
    except:
        pass
    
    h7 = controller.net.get('h7')
    h7.cmd('ip route del default 2>/dev/null || true')
    h7.cmd('ip route add default via 10.2.2.253')
    h7.cmd('ip route add 10.2.1.0/24 via 10.2.2.253 metric 1')
    h7.cmd('ip route add 10.1.0.0/16 via 10.2.2.253 metric 1')
    
    h8 = controller.net.get('h8')
    h8.cmd('ip route del default 2>/dev/null || true')
    h8.cmd('ip route add default via 10.2.2.253')
    h8.cmd('ip route add 10.2.1.0/24 via 10.2.2.253 metric 1')
    h8.cmd('ip route add 10.1.0.0/16 via 10.2.2.253 metric 1')
    
    h5 = controller.net.get('h5')
    h5.cmd('ip route del default 2>/dev/null || true')
    h5.cmd('ip route add default via 10.2.1.254')
    h5.cmd('ip route add 10.2.2.0/24 via 10.2.1.254 metric 1')
    h5.cmd('ip route add 10.1.0.0/16 via 10.2.1.254 metric 1')
    
    h6 = controller.net.get('h6')
    h6.cmd('ip route del default 2>/dev/null || true')
    h6.cmd('ip route add default via 10.2.1.254')
    h6.cmd('ip route add 10.2.2.0/24 via 10.2.1.254 metric 1')
    h6.cmd('ip route add 10.1.0.0/16 via 10.2.1.254 metric 1')
    
    ar3 = controller.net.get('ar3')
    ar3.cmd('ip route del 10.2.2.0/24 2>/dev/null || true')
    ar3.cmd('ip route add 10.2.2.0/24 dev ar3-eth3 metric 1')
    ar3.cmd('ip route add 10.1.1.0/24 via 172.16.3.1 metric 1')
    ar3.cmd('ip route add 10.1.2.0/24 via 172.16.3.1 metric 1')
    
    cr1 = controller.net.get('cr1')
    cr1.cmd('ip route add 10.2.2.0/24 via 172.16.3.2 metric 1')
    
    ar1 = controller.net.get('ar1')
    ar1.cmd('ip route del 10.2.2.0/24 2>/dev/null || true')
    ar1.cmd('ip route add 10.2.2.0/24 via 172.16.1.1 metric 1')
    ar1.cmd('ip route del 10.2.1.0/24 2>/dev/null || true')
    ar1.cmd('ip route add 10.2.1.0/24 via 172.16.1.1 metric 1')
    
    ar2 = controller.net.get('ar2')
    ar2.cmd('ip route del 10.2.2.0/24 2>/dev/null || true')
    ar2.cmd('ip route add 10.2.2.0/24 via 10.1.2.253 metric 1')
    ar2.cmd('ip route del 10.2.1.0/24 2>/dev/null || true')
    ar2.cmd('ip route add 10.2.1.0/24 via 10.1.2.253 metric 1')
    
    print("✅ AR4 failure recovery complete")

def fix_cr1_complete_failure(controller):
    """Fix complete CR1 core router failure"""
    print("🔧 Fixing complete CR1 failure...")
    
    try:
        controller.net.configLinkStatus('cr1', 'ar1', 'down')
        controller.net.configLinkStatus('cr1', 'ar3', 'down')
    except:
        pass
    
    ar1 = controller.net.get('ar1')
    ar1.cmd('ip route del 10.2.0.0/16 2>/dev/null || true')
    ar1.cmd('ip route add 10.2.0.0/16 via 10.1.1.253 metric 1')
    
    ar3 = controller.net.get('ar3')
    ar3.cmd('ip route del 10.1.0.0/16 2>/dev/null || true')
    ar3.cmd('ip route add 10.1.0.0/16 via 10.2.1.253 metric 1')
    
    ar2 = controller.net.get('ar2')
    ar2.cmd('ip route add 10.2.1.0/24 via 172.16.6.1 metric 1')
    ar2.cmd('ip route add 10.2.2.0/24 via 172.16.6.1 metric 1')
    
    ar4 = controller.net.get('ar4')
    ar4.cmd('ip route add 10.1.1.0/24 via 172.16.8.1 metric 1')
    ar4.cmd('ip route add 10.1.2.0/24 via 172.16.8.1 metric 1')
    
    cr2 = controller.net.get('cr2')
    cr2.cmd('ip route add 10.1.1.0/24 via 172.16.6.2 metric 1')
    cr2.cmd('ip route add 10.1.2.0/24 via 172.16.6.2 metric 1')
    cr2.cmd('ip route add 10.2.1.0/24 via 172.16.8.2 metric 1')
    cr2.cmd('ip route add 10.2.2.0/24 via 172.16.8.2 metric 1')
    
    print("✅ CR1 failure recovery complete")

def fix_cr2_complete_failure(controller):
    """Fix complete CR2 core router failure"""
    print("🔧 Fixing complete CR2 failure...")
    
    try:
        controller.net.configLinkStatus('cr2', 'ar2', 'down')
        controller.net.configLinkStatus('cr2', 'ar4', 'down')
    except:
        pass
    
    ar2 = controller.net.get('ar2')
    ar2.cmd('ip route del 10.2.0.0/16 2>/dev/null || true')
    ar2.cmd('ip route add 10.2.0.0/16 via 10.1.2.253 metric 1')
    
    ar4 = controller.net.get('ar4')
    ar4.cmd('ip route del 10.1.0.0/16 2>/dev/null || true')
    ar4.cmd('ip route add 10.1.0.0/16 via 10.2.2.253 metric 1')
    
    ar1 = controller.net.get('ar1')
    ar1.cmd('ip route add 10.2.1.0/24 via 172.16.1.1 metric 1')
    ar1.cmd('ip route add 10.2.2.0/24 via 172.16.1.1 metric 1')
    
    ar3 = controller.net.get('ar3')
    ar3.cmd('ip route add 10.1.1.0/24 via 172.16.3.1 metric 1')
    ar3.cmd('ip route add 10.1.2.0/24 via 172.16.3.1 metric 1')
    
    cr1 = controller.net.get('cr1')
    cr1.cmd('ip route add 10.1.1.0/24 via 172.16.1.2 metric 1')
    cr1.cmd('ip route add 10.1.2.0/24 via 172.16.1.2 metric 1')
    cr1.cmd('ip route add 10.2.1.0/24 via 172.16.3.2 metric 1')
    cr1.cmd('ip route add 10.2.2.0/24 via 172.16.3.2 metric 1')
    
    print("✅ CR2 failure recovery complete")

def detect_link_failure(controller, node1, node2):
    """Detect if a specific link between two nodes is down"""
    try:
        for link in controller.net.links:
            link_nodes = [link.intf1.node.name, link.intf2.node.name]
            if (node1 in link_nodes and node2 in link_nodes):
                intf1_up = link.intf1.isUp()
                intf2_up = link.intf2.isUp()
                return not (intf1_up and intf2_up)
        return False
    except Exception as e:
        return False

def auto_detect_and_fix_failures(controller):
    """Automatically detect specific link failures and apply appropriate fixes"""
    print("🤖 AUTO-DETECTING SPECIFIC LINK FAILURES...")
    print("=" * 45)
    
    fixes_applied = []
    
    if detect_link_failure(controller, 'ar1', 'es1'):
        print("🔍 AR1↔ES1 LINK FAILURE DETECTED - removing AR1...")
        fix_ar1_complete_failure(controller)
        fixes_applied.append("AR1 (ar1↔es1 failed)")
    
    elif detect_link_failure(controller, 'ar1', 'es2'):
        print("🔍 AR1↔ES2 LINK FAILURE DETECTED - removing AR1...")
        fix_ar1_complete_failure(controller)
        fixes_applied.append("AR1 (ar1↔es2 failed)")
    
    elif detect_link_failure(controller, 'ar2', 'es1'):
        print("🔍 AR2↔ES1 LINK FAILURE DETECTED - removing AR2...")
        fix_ar2_complete_failure(controller)
        fixes_applied.append("AR2 (ar2↔es1 failed)")
    
    elif detect_link_failure(controller, 'ar2', 'es2'):
        print("🔍 AR2↔ES2 LINK FAILURE DETECTED - removing AR2...")
        fix_ar2_complete_failure(controller)
        fixes_applied.append("AR2 (ar2↔es2 failed)")
    
    elif detect_link_failure(controller, 'ar3', 'es3'):
        print("🔍 AR3↔ES3 LINK FAILURE DETECTED - removing AR3...")
        fix_ar3_complete_failure(controller)
        fixes_applied.append("AR3 (ar3↔es3 failed)")
    
    elif detect_link_failure(controller, 'ar3', 'es4'):
        print("🔍 AR3↔ES4 LINK FAILURE DETECTED - removing AR3...")
        fix_ar3_complete_failure(controller)
        fixes_applied.append("AR3 (ar3↔es4 failed)")
    
    elif detect_link_failure(controller, 'ar4', 'es3'):
        print("🔍 AR4↔ES3 LINK FAILURE DETECTED - removing AR4...")
        fix_ar4_complete_failure(controller)
        fixes_applied.append("AR4 (ar4↔es3 failed)")
    
    elif detect_link_failure(controller, 'ar4', 'es4'):
        print("🔍 AR4↔ES4 LINK FAILURE DETECTED - removing AR4...")
        fix_ar4_complete_failure(controller)
        fixes_applied.append("AR4 (ar4↔es4 failed)")
    
    elif detect_link_failure(controller, 'ar1', 'cr1'):
        print("🔍 AR1↔CR1 LINK FAILURE DETECTED - removing CR1...")
        fix_cr1_complete_failure(controller)
        fixes_applied.append("CR1 (ar1↔cr1 failed)")
    
    elif detect_link_failure(controller, 'ar2', 'cr2'):
        print("🔍 AR2↔CR2 LINK FAILURE DETECTED - removing CR2...")
        fix_cr2_complete_failure(controller)
        fixes_applied.append("CR2 (ar2↔cr2 failed)")
    
    elif detect_link_failure(controller, 'ar3', 'cr1'):
        print("🔍 AR3↔CR1 LINK FAILURE DETECTED - removing CR1...")
        fix_cr1_complete_failure(controller)
        fixes_applied.append("CR1 (ar3↔cr1 failed)")
    
    elif detect_link_failure(controller, 'ar4', 'cr2'):
        print("🔍 AR4↔CR2 LINK FAILURE DETECTED - removing CR2...")
        fix_cr2_complete_failure(controller)
        fixes_applied.append("CR2 (ar4↔cr2 failed)")
    
    if fixes_applied:
        print(f"⚡ APPLIED AUTO-FIXES: {', '.join(fixes_applied)}")
        time.sleep(2)
        
        print("\n🧪 VERIFYING AUTO-FIX RESULTS:")
        test_pairs = [
            ('h1', 'h3'), ('h1', 'h5'), ('h3', 'h5'),
            ('h5', 'h7'), ('h7', 'h1'), ('h5', 'h3')
        ]
        
        all_working = True
        for src, dst in test_pairs:
            success = controller.router_manager.test_connectivity(src, dst)
            status = "✅" if success else "❌"
            print(f"   {status} {src} → {dst}")
            if not success:
                all_working = False
        
        if all_working:
            print("🎉 AUTO-FIX SUCCESSFUL! All connections working!")
        else:
            print("⚠️ Some connections still failing")
        
        return all_working
    else:
        print("✅ No link failures detected - network is healthy")
        return True
