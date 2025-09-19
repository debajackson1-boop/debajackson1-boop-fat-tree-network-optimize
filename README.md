# SDN Fat-Tree Network - Complete Installation Guide

## What is this project?

This is a comprehensive Software-Defined Networking (SDN) solution that creates and manages a Fat-Tree network topology using Mininet. The system provides:

- **Fat-Tree Network Topology**: A hierarchical network structure with 2 core routers, 4 aggregation routers, 4 edge switches, and 8 hosts
- **Real-time Web Dashboard**: Browser-based interface for monitoring and controlling the network
- **AI-Powered Optimization**: TensorFlow neural network that learns to optimize network latency
- **Container Monitoring**: Integration with Docker to monitor container performance
- **Professional Testing**: Industry-standard testing including CBench and IEEE 802.1Q compliance
- **Automated Failure Recovery**: Intelligent detection and repair of network failures

## How it works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Web Dashboard (Flask)                        │
│              http://localhost:5000                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ REST API / File Communication
┌─────────────────────▼───────────────────────────────────────────┐
│                Main Controller                                  │
│  • Network topology management                                 │
│  • Routing decisions                                           │
│  • Failure detection & recovery                               │
│  • Neural optimizer integration                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │ OpenFlow Protocol
┌─────────────────────▼───────────────────────────────────────────┐
│                Fat-Tree Topology                               │
│                                                                │
│     Core Layer:     [CR1] ──── [CR2]                          │
│                      │    ╲╱    │                              │
│  Aggregation:      [AR1] ── [AR2] [AR3] ── [AR4]              │
│                      │  ╲╱  │     │  ╲╱  │                     │
│     Edge Layer:    [ES1] ── [ES2] [ES3] ── [ES4]              │
│                      │       │     │       │                   │
│     Hosts:         [H1,H2] [H3,H4] [H5,H6] [H7,H8]            │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Main Controller** (`main_controller.py`): Core network management logic
2. **Fat-Tree Topology** (`fat_tree_topology.py`): Network structure definition
3. **Web Dashboard** (`working_dashboard.py`): User interface for monitoring/control
4. **Neural Optimizer** (`sophisticated_latency_neural_optimizer.py`): AI-based optimization
5. **Monitoring System** (`network_statistics_monitor.py`): Real-time data collection
6. **Container Integration** (`container_stats_addon.py`): Docker monitoring
7. **Testing Suite** (`professional_sdn_testing_suite.py`): Performance validation

## Requirements

### System Requirements
- **Operating System**: Ubuntu 16.04, 18.04, 20.04 (pip works without virtual environment), or Ubuntu 22.04+ (virtual environment recommended)
- **Python**: 3.8 or higher required for TensorFlow compatibility
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies and logs
- **Network**: Internet connection for package installation

### Required System Packages
- python3, python3-pip, python3-venv
- mininet, openvswitch-switch
- iperf3, netperf (for network testing)
- docker.io (optional, for container monitoring)
- build-essential (for compiling some Python packages)

### Required Python Packages
- flask (web dashboard framework)
- requests (HTTP communication between components)
- numpy (numerical computations for neural networks)
- tensorflow (AI-powered network optimization)
- psutil (system and process monitoring)

## Installation Instructions

### Ubuntu 20.04 and Earlier (Direct pip installation - Recommended)

**Step 1: Update system and install dependencies**
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip build-essential
sudo apt install -y mininet openvswitch-switch openvswitch-common
sudo apt install -y iperf3 netperf docker.io
sudo apt install -y net-tools curl wget git
```

**Step 2: Start required services**
```bash
sudo systemctl start openvswitch-switch
sudo systemctl enable openvswitch-switch
sudo systemctl start docker
sudo systemctl enable docker
```

**Step 3: Create project directory**
```bash
mkdir ~/sdn-fat-tree-network
cd ~/sdn-fat-tree-network
```

**Step 4: Install Python packages directly (no virtual environment needed)**
```bash
sudo pip3 install --upgrade pip
sudo pip3 install flask>=2.0.0
sudo pip3 install requests>=2.25.0
sudo pip3 install numpy>=1.20.0
sudo pip3 install tensorflow>=2.8.0
sudo pip3 install psutil>=5.8.0
```

### Ubuntu 22.04 and Newer (Virtual Environment Recommended)

**Step 1: Update system and install dependencies**
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv build-essential
sudo apt install -y mininet openvswitch-switch openvswitch-common
sudo apt install -y iperf3 netperf docker.io
sudo apt install -y net-tools curl wget git
```

**Step 2: Start required services**
```bash
sudo systemctl start openvswitch-switch
sudo systemctl enable openvswitch-switch
sudo systemctl start docker
sudo systemctl enable docker
```

**Step 3: Create project directory and virtual environment**
```bash
mkdir ~/sdn-fat-tree-network
cd ~/sdn-fat-tree-network
python3 -m venv venv
source venv/bin/activate
```

**Step 4: Install Python packages in virtual environment**
```bash
pip install --upgrade pip
pip install flask>=2.0.0
pip install requests>=2.25.0
pip install numpy>=1.20.0
pip install tensorflow>=2.8.0
pip install psutil>=5.8.0
```

### Ubuntu 16.04 (Manual Python upgrade required)

**Step 1: Install Python 3.8+**
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8 python3.8-dev
sudo apt install python3-pip build-essential
```

**Step 2: Install system dependencies**
```bash
sudo apt install -y openvswitch-switch openvswitch-common
sudo apt install -y iperf3 netperf docker.io
sudo apt install -y net-tools curl wget git

# Install Mininet manually (not in Ubuntu 16.04 repos)
git clone https://github.com/mininet/mininet
cd mininet
git checkout -b mininet-2.3.0 2.3.0
./util/install.sh -a
cd ..
rm -rf mininet
```

**Step 3: Create project directory**
```bash
mkdir ~/sdn-fat-tree-network
cd ~/sdn-fat-tree-network
```

**Step 4: Install Python packages directly**
```bash
sudo pip3 install --upgrade pip
sudo pip3 install flask>=2.0.0
sudo pip3 install requests>=2.25.0
sudo pip3 install numpy>=1.20.0
sudo pip3 install tensorflow>=2.8.0
sudo pip3 install psutil>=5.8.0
```

## Adding Your Code Files

Copy all your Python files to the project directory:
```bash
# Copy your .py files here
# For example:
# cp /path/to/your/files/*.py ~/sdn-fat-tree-network/
```

## Running the System

### For Ubuntu 20.04 and Earlier (Direct installation)

**Step 1: Start the main controller**
```bash
# Navigate to project directory
cd ~/sdn-fat-tree-network

# Start the main controller
sudo python3 main_controller.py
```

**Step 2: Start the dashboard (new terminal)**
```bash
# Navigate to project directory
cd ~/sdn-fat-tree-network

# Start the dashboard
python3 dashboard_core.py
```

### For Ubuntu 22.04 and Newer (Virtual environment)

**Step 1: Start the main controller**
```bash
# Navigate to project directory
cd ~/sdn-fat-tree-network

# Activate virtual environment
source venv/bin/activate

# Start the main controller
sudo $(which python3) main_controller.py
```

**Step 2: Start the dashboard (new terminal)**
```bash
# Navigate to project directory
cd ~/sdn-fat-tree-network

# Activate virtual environment
source venv/bin/activate

# Start the dashboard
python3 dashboard_core.py
```

**Step 3: Open the browser**
Visit: http://localhost:5000

## Features

The system automatically handles:
- **Network Statistics Collection**: Traffic, latency, and performance metrics
- **Container Monitoring**: Docker container resource usage tracking  
- **Historical Data Logging**: CSV files with network performance history
- **Failure Detection**: Automatic identification of network issues
- **Real-time Dashboard Updates**: Live network visualization and status

All logging and monitoring runs automatically once the system starts.

## Verification Commands

Test your installation:
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check Mininet
sudo mn --version

# Check OpenFlow
sudo ovs-vsctl show

# Check Docker
docker --version

# Test Python packages
python3 -c "
import flask, requests, numpy, tensorflow, psutil
print('Flask:', flask.__version__)
print('TensorFlow:', tensorflow.__version__)
print('NumPy:', numpy.__version__)
print('All packages working!')
"

# Test basic Mininet functionality
sudo mn --test pingall
```

## Ubuntu Version Summary

- **Ubuntu 16.04**: Requires manual Python 3.8+ installation, pip works directly
- **Ubuntu 18.04**: Python 3.6+ available, pip works directly
- **Ubuntu 20.04**: Python 3.8+ available, pip works directly (recommended approach)
- **Ubuntu 22.04+**: Virtual environment recommended due to newer pip restrictions

## File Structure

```
sdn-fat-tree-network/
├── main_controller.py              # Main network controller
├── fat_tree_topology.py           # Network topology definition
├── working_dashboard.py           # Web dashboard with command execution
├── sophisticated_latency_neural_optimizer.py  # AI optimization with ON/OFF toggle
├── network_statistics_monitor.py  # Monitoring system with real ping measurements
├── container_stats_addon.py       # Container monitoring (referenced)
├── professional_sdn_testing_suite.py  # Testing framework (CBench, IEEE 802.1Q, Business Load)
├── router_config.py               # Router configuration and utilities
├── fat_tree_autofix.py           # Automatic failure recovery (referenced)
├── monitoring_toggle.py           # Verbose monitoring control
├── network_logger.py              # Historical data logging to CSV files
├── stats_dashboard_extension.py   # Statistics dashboard extension
├── stats_integration.py           # Simple stats integration for controllers
├── test_stats_collection.py       # Test script for statistics collection
├── real_latency_only_fix.py       # Real ping measurements only (no simulation)
└── auto_monitoring_integration.py # Automatic monitoring startup/cleanup
```

### File Descriptions

**Core System:**
- `main_controller.py` - Main Fat-Tree controller with basic functionality and error suppression
- `fat_tree_topology.py` - Creates 2-core, 4-aggregation, 4-edge, 8-host Fat-Tree topology
- `router_config.py` - LinuxRouter class and routing configuration utilities

**Web Interface:**
- `working_dashboard.py` - Complete web dashboard with controller communication
- `stats_dashboard_extension.py` - Statistics visualization dashboard extension

**AI Optimization:**
- `sophisticated_latency_neural_optimizer.py` - TensorFlow neural network with ON/OFF toggle for latency optimization

**Automation & Integration:**
- `auto_monitoring_integration.py` - Automatic monitoring startup and cleanup
- `stats_integration.py` - Simple stats integration for existing controllers
- `monitoring_toggle.py` - Enable/disable verbose monitoring messages

**Testing:**
- `professional_sdn_testing_suite.py` - CBench, IEEE 802.1Q QoS, business load tests
- `test_stats_collection.py` - Generate network activity and test statistics collection

**Data Files (Auto-generated):**
```
network_stats/                     # Current statistics (CSV)
├── traffic_stats.csv
├── latency_stats.csv
├── admission_stats.csv
└── link_utilization.csv

network_logs/                      # Historical logs
├── traffic_history.csv
├── latency_history.csv
├── health_history.csv
├── events.log
└── daily_summary_YYYYMMDD.json
```

## What Each Package Does

- **flask**: Web dashboard framework for real-time network monitoring
- **requests**: HTTP communication between dashboard and controller components
- **numpy**: Numerical computations required by TensorFlow for neural networks
- **tensorflow**: AI-powered latency optimization and network performance learning
- **psutil**: System monitoring, process management, and resource tracking

All other imports (json, csv, subprocess, threading, time, os, re, statistics, random, collections, datetime) are built-in Python modules requiring no installation.

## License

This project is licensed under the MIT License - anyone can use it for any purpose with attribution.
