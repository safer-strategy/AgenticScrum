#!/bin/bash

# Smart Development Environment Manager
# Optimizes the balance between speed and production parity

# Create development environment manager
cat > /usr/local/bin/dev-env << 'EOF'
#!/bin/bash

# Development Environment Smart Manager
set -e

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CONFIG_FILE="$PROJECT_ROOT/.dev-env.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect project type
detect_project_type() {
    if [[ -f "package.json" ]]; then
        echo "node"
    elif [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        echo "python"
    elif [[ -f "go.mod" ]]; then
        echo "go"
    else
        echo "unknown"
    fi
}

# Smart service starter
start_services() {
    local mode=${1:-auto}
    local project_type=$(detect_project_type)
    
    echo -e "${BLUE}Starting development environment...${NC}"
    
    # Always start infrastructure services
    if [[ -f "docker-compose.infra.yml" ]]; then
        echo "Starting infrastructure services..."
        docker-compose -f docker-compose.infra.yml up -d
    elif [[ -f "docker-compose.yml" ]]; then
        # Parse and start only non-app services
        echo "Starting background services..."
        docker-compose up -d postgres redis elasticsearch rabbitmq mongo 2>/dev/null || true
    fi
    
    # Start application based on mode
    case $mode in
        "native"|"fast")
            echo -e "${GREEN}Starting application natively...${NC}"
            start_native_app $project_type
            ;;
        "docker"|"container")
            echo -e "${GREEN}Starting application in container...${NC}"
            docker-compose up -d
            ;;
        "auto")
            # Smart detection based on context
            if is_debugging || is_heavy_development; then
                start_native_app $project_type
            else
                docker-compose up -d
            fi
            ;;
    esac
}

# Start native application
start_native_app() {
    local project_type=$1
    
    case $project_type in
        "node")
            if [[ -f ".nvmrc" ]]; then
                nvm use
            fi
            npm install
            npm run dev &
            echo $! > .dev-env.pid
            ;;
        "python")
            if [[ -f ".python-version" ]]; then
                pyenv local $(cat .python-version)
            fi
            if [[ ! -d "venv" ]]; then
                python -m venv venv
            fi
            source venv/bin/activate
            pip install -r requirements.txt
            if [[ -f "main.py" ]]; then
                uvicorn main:app --reload &
            else
                python app.py &
            fi
            echo $! > .dev-env.pid
            ;;
    esac
}

# Check if in debugging mode
is_debugging() {
    # Check for common debug indicators
    [[ -n "${DEBUG}" ]] || \
    [[ -f ".vscode/launch.json" ]] || \
    [[ -n "$(pgrep -f 'node.*inspect')" ]]
}

# Check if heavy development (many file changes)
is_heavy_development() {
    # Check git status for many changes
    local changes=$(git status --porcelain 2>/dev/null | wc -l)
    [[ $changes -gt 10 ]]
}

# Stop all services
stop_services() {
    echo -e "${YELLOW}Stopping development environment...${NC}"
    
    # Stop native app if running
    if [[ -f ".dev-env.pid" ]]; then
        kill $(cat .dev-env.pid) 2>/dev/null || true
        rm .dev-env.pid
    fi
    
    # Stop containers
    docker-compose down
}

# Status check
status() {
    echo -e "${BLUE}=== Development Environment Status ===${NC}"
    
    # Check native app
    if [[ -f ".dev-env.pid" ]] && kill -0 $(cat .dev-env.pid) 2>/dev/null; then
        echo -e "${GREEN}✓ Native app running (PID: $(cat .dev-env.pid))${NC}"
    else
        echo -e "${YELLOW}✗ Native app not running${NC}"
    fi
    
    # Check containers
    echo -e "\n${BLUE}Container Services:${NC}"
    docker-compose ps --services --filter "status=running" 2>/dev/null || echo "No containers running"
}

# Sync environment
sync_env() {
    echo -e "${BLUE}Syncing development environment...${NC}"
    
    # Sync database
    if command -v dbmate &> /dev/null; then
        dbmate up
    fi
    
    # Sync dependencies
    local project_type=$(detect_project_type)
    case $project_type in
        "node")
            npm install
            ;;
        "python")
            pip install -r requirements.txt
            ;;
    esac
}

# Performance profiler
profile() {
    local mode=${1:-native}
    echo -e "${BLUE}Profiling $mode startup time...${NC}"
    
    case $mode in
        "native")
            time (
                start_services native
                sleep 5
                stop_services
            )
            ;;
        "docker")
            time (
                docker-compose up -d
                sleep 5
                docker-compose down
            )
            ;;
    esac
}

# Main command handler
case ${1:-help} in
    start)
        start_services ${2:-auto}
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services ${2:-auto}
        ;;
    status)
        status
        ;;
    sync)
        sync_env
        ;;
    profile)
        profile ${2:-native}
        ;;
    help|*)
        echo "Usage: dev-env [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start [auto|native|docker]  - Start development environment"
        echo "  stop                        - Stop all services"
        echo "  restart                     - Restart environment"
        echo "  status                      - Show environment status"
        echo "  sync                        - Sync dependencies and database"
        echo "  profile [native|docker]     - Profile startup performance"
        echo ""
        echo "Modes:"
        echo "  auto    - Smart detection (default)"
        echo "  native  - Run app natively, infra in containers"
        echo "  docker  - Everything in containers"
        ;;
esac
EOF

chmod +x /usr/local/bin/dev-env

# Create smart docker-compose splitter
cat > /usr/local/bin/split-compose << 'EOF'
#!/usr/bin/env python3

import yaml
import sys
import os

def split_compose(input_file):
    """Split docker-compose.yml into app and infra components"""
    
    with open(input_file, 'r') as f:
        compose = yaml.safe_load(f)
    
    # Define infrastructure services
    infra_services = {
        'postgres', 'postgresql', 'mysql', 'mariadb', 'mongodb', 'mongo',
        'redis', 'memcached', 'elasticsearch', 'elastic', 'kibana',
        'rabbitmq', 'kafka', 'zookeeper', 'consul', 'vault',
        'prometheus', 'grafana', 'jaeger', 'zipkin',
        'nginx', 'traefik', 'haproxy', 'envoy',
        'localstack', 'minio', 'mailhog', 'adminer'
    }
    
    infra_compose = {
        'version': compose.get('version', '3'),
        'services': {},
        'volumes': compose.get('volumes', {}),
        'networks': compose.get('networks', {})
    }
    
    app_compose = {
        'version': compose.get('version', '3'),
        'services': {},
        'networks': compose.get('networks', {})
    }
    
    # Split services
    for service_name, service_config in compose.get('services', {}).items():
        if service_name in infra_services or 'image' in service_config:
            # External images go to infra
            infra_compose['services'][service_name] = service_config
        else:
            # Built services go to app
            app_compose['services'][service_name] = service_config
    
    # Write split files
    with open('docker-compose.infra.yml', 'w') as f:
        yaml.dump(infra_compose, f, default_flow_style=False)
    
    with open('docker-compose.app.yml', 'w') as f:
        yaml.dump(app_compose, f, default_flow_style=False)
    
    print("✓ Created docker-compose.infra.yml")
    print("✓ Created docker-compose.app.yml")

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'docker-compose.yml'
    if os.path.exists(input_file):
        split_compose(input_file)
    else:
        print(f"Error: {input_file} not found")
        sys.exit(1)
EOF

chmod +x /usr/local/bin/split-compose

# Create development mode switcher
cat > /usr/local/bin/dev-mode << 'EOF'
#!/bin/bash

# Development Mode Configuration Manager

MODE_FILE="$HOME/.dev-mode"
CURRENT_MODE=$(cat $MODE_FILE 2>/dev/null || echo "hybrid")

case ${1:-show} in
    native)
        echo "native" > $MODE_FILE
        echo "Switched to NATIVE mode - maximum speed, apps run on host"
        ;;
    docker)
        echo "docker" > $MODE_FILE
        echo "Switched to DOCKER mode - full containerization"
        ;;
    hybrid)
        echo "hybrid" > $MODE_FILE
        echo "Switched to HYBRID mode - smart balance"
        ;;
    show)
        echo "Current development mode: $CURRENT_MODE"
        echo ""
        echo "Available modes:"
        echo "  native - Run apps natively, infra in Docker (fastest)"
        echo "  docker - Everything in containers (prod-like)"
        echo "  hybrid - Smart switching based on context (default)"
        ;;
esac
EOF

chmod +x /usr/local/bin/dev-mode

# Create performance monitoring script
cat > /usr/local/bin/dev-perf << 'EOF'
#!/bin/bash

# Monitor development environment performance

echo "=== Development Environment Performance ==="
echo ""

# Container overhead
if command -v docker &> /dev/null; then
    echo "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo ""
fi

# Process monitoring
echo "Top Development Processes:"
ps aux | grep -E "(node|python|docker|java)" | head -5
echo ""

# Startup time comparison
echo "Estimated Startup Times:"
echo "  Native Node.js:    ~3 seconds"
echo "  Native Python:     ~2 seconds"
echo "  Docker Compose:    ~30-60 seconds"
echo "  Docker (cached):   ~10-20 seconds"
echo ""

# Memory usage
echo "Memory Usage:"
free -h
EOF

chmod +x /usr/local/bin/dev-perf

# Install development optimization tools
apt-get update && apt-get install -y \
    inotify-tools \
    entr \
    watchman

# Install Skaffold for smart container development
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
install skaffold /usr/local/bin/
rm skaffold

# Create example configuration
cat > /opt/dev/configs/dev-env-example.json << 'EOF'
{
  "project": "casari",
  "defaultMode": "hybrid",
  "services": {
    "always_container": ["postgres", "redis", "elasticsearch"],
    "prefer_native": ["api", "frontend", "worker"],
    "auto_detect": true
  },
  "performance": {
    "lazy_load": true,
    "cache_dependencies": true,
    "hot_reload": true
  },
  "agenticScrum": {
    "enabled": true,
    "auto_optimize": true,
    "profile_threshold_ms": 5000
  }
}
EOF

echo ""
echo "=== Smart Development Environment Installed ==="
echo ""
echo "New commands available:"
echo "  dev-env start    - Smart environment starter"
echo "  dev-mode         - Switch between native/docker/hybrid"
echo "  split-compose    - Split compose file into app/infra"
echo "  dev-perf         - Monitor performance"
echo ""
echo "Example workflow:"
echo "  1. dev-mode hybrid"
echo "  2. split-compose"
echo "  3. dev-env start"
echo ""