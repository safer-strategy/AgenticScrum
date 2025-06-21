#!/bin/bash

# Ubuntu Dev Lab Setup Script for Casari Project
# Designed for AgenticScrum framework deployment
# Author: DevOps Setup Script
# Version: 1.0

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "================================================"
echo "   Ubuntu Dev Lab Setup for Casari Project     "
echo "   AgenticScrum Framework Deployment            "
echo "================================================"
echo -e "${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
   exit 1
fi

# Get system information
log "Gathering system configuration..."

# Interactive configuration
echo -e "${BLUE}=== System Configuration ===${NC}"

# Hostname
read -p "Enter hostname for this VM [ub00]: " HOSTNAME
HOSTNAME=${HOSTNAME:-ub00}

# IP Configuration
read -p "Enter static IP address (or press Enter for DHCP): " STATIC_IP
if [[ -n "$STATIC_IP" ]]; then
    read -p "Enter netmask [255.255.255.0]: " NETMASK
    NETMASK=${NETMASK:-255.255.255.0}
    read -p "Enter gateway: " GATEWAY
    read -p "Enter network interface name [$(ip -o -4 route show to default | awk '{print $5}')]: " INTERFACE
    INTERFACE=${INTERFACE:-$(ip -o -4 route show to default | awk '{print $5}')}
fi

# DNS Configuration
read -p "Enter primary DNS server [8.8.8.8]: " DNS1
DNS1=${DNS1:-8.8.8.8}
read -p "Enter secondary DNS server [8.8.4.4]: " DNS2
DNS2=${DNS2:-8.8.4.4}

# Docker configuration
read -p "Install Docker? [Y/n]: " INSTALL_DOCKER
INSTALL_DOCKER=${INSTALL_DOCKER:-Y}

# Kubernetes configuration
read -p "Install Kubernetes (kubectl, minikube, k3s)? [Y/n]: " INSTALL_K8S
INSTALL_K8S=${INSTALL_K8S:-Y}

# Development tools configuration
read -p "Install Python development tools? [Y/n]: " INSTALL_PYTHON
INSTALL_PYTHON=${INSTALL_PYTHON:-Y}

read -p "Install Node.js and npm? [Y/n]: " INSTALL_NODE
INSTALL_NODE=${INSTALL_NODE:-Y}

# Apply hostname
log "Setting hostname to $HOSTNAME..."
hostnamectl set-hostname $HOSTNAME
echo "127.0.1.1 $HOSTNAME" >> /etc/hosts

# Configure network if static IP requested
if [[ -n "$STATIC_IP" ]]; then
    log "Configuring static IP address..."
    
    # Create netplan configuration
    cat > /etc/netplan/01-netcfg.yaml <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: false
      addresses:
        - $STATIC_IP/${NETMASK##*.}
      gateway4: $GATEWAY
      nameservers:
        addresses: [$DNS1, $DNS2]
EOF
    
    netplan apply
else
    log "Using DHCP configuration..."
fi

# Configure DNS
log "Configuring DNS..."
cat > /etc/resolv.conf <<EOF
nameserver $DNS1
nameserver $DNS2
EOF

# Update system
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install essential packages
log "Installing essential development packages..."
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    net-tools \
    dnsutils \
    iputils-ping \
    openssh-server \
    openssh-client \
    jq \
    tree \
    unzip \
    zip \
    gzip \
    tar \
    tmux \
    screen \
    ncdu \
    iotop \
    sysstat \
    bash-completion \
    python3-pip \
    python3-venv \
    make \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    python3-dev

# Install Docker
if [[ "$INSTALL_DOCKER" =~ ^[Yy]$ ]]; then
    log "Installing Docker..."
    
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    usermod -aG docker $SUDO_USER || true
    
    # Enable and start Docker
    systemctl enable docker
    systemctl start docker
    
    # Install Docker Compose standalone
    log "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install Kubernetes tools
if [[ "$INSTALL_K8S" =~ ^[Yy]$ ]]; then
    log "Installing Kubernetes tools..."
    
    # Install kubectl
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
    
    # Install minikube
    log "Installing Minikube..."
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64
    
    # Install k3s (lightweight Kubernetes)
    log "Installing k3s..."
    curl -sfL https://get.k3s.io | sh -
    
    # Install Helm
    log "Installing Helm..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    
    # Install k9s (Kubernetes CLI UI)
    log "Installing k9s..."
    wget -q https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_amd64.tar.gz
    tar -xzf k9s_Linux_amd64.tar.gz
    mv k9s /usr/local/bin/
    rm k9s_Linux_amd64.tar.gz
fi

# Install Python development tools
if [[ "$INSTALL_PYTHON" =~ ^[Yy]$ ]]; then
    log "Installing Python development tools..."
    
    # Install pyenv for Python version management
    git clone https://github.com/pyenv/pyenv.git /opt/pyenv
    
    # Install common Python packages
    pip3 install --upgrade pip
    pip3 install \
        virtualenv \
        pipenv \
        poetry \
        black \
        flake8 \
        pylint \
        pytest \
        requests \
        pandas \
        numpy \
        jupyter \
        ipython
fi

# Install Node.js and npm
if [[ "$INSTALL_NODE" =~ ^[Yy]$ ]]; then
    log "Installing Node.js and npm..."
    
    # Install Node.js 20.x
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    
    # Install Yarn
    npm install -g yarn
    
    # Install common global packages
    npm install -g \
        typescript \
        ts-node \
        nodemon \
        pm2 \
        express-generator \
        create-react-app \
        @angular/cli \
        vue-cli
fi

# Install additional development tools
log "Installing additional development tools..."

# Install Go
log "Installing Go..."
wget -q https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
rm go1.21.5.linux-amd64.tar.gz

# Install Rust
log "Installing Rust..."
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install VS Code CLI
log "Installing VS Code CLI..."
curl -fsSL https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64 | tar -xz -C /usr/local/bin

# Install GitHub CLI
log "Installing GitHub CLI..."
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt update
apt install gh -y

# Clone AgenticScrum framework
log "Cloning AgenticScrum framework..."
if [[ -n "$SUDO_USER" ]]; then
    USER_HOME=$(getent passwd $SUDO_USER | cut -d: -f6)
    sudo -u $SUDO_USER git clone https://github.com/safer-strategy/AgenticScrum.git $USER_HOME/AgenticScrum
else
    git clone https://github.com/safer-strategy/AgenticScrum.git /root/AgenticScrum
fi

# Setup environment variables
log "Setting up environment variables..."
cat >> /etc/profile.d/devlab.sh <<'EOF'
# Development Lab Environment Variables
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
export PATH=$PATH:$HOME/.cargo/bin
export PYENV_ROOT="/opt/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Kubernetes aliases
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployment'
alias kaf='kubectl apply -f'
alias kdel='kubectl delete'
alias klog='kubectl logs'
alias kexec='kubectl exec -it'

# Docker aliases
alias d='docker'
alias dc='docker-compose'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'
alias dl='docker logs'
alias drm='docker rm $(docker ps -aq)'
alias drmi='docker rmi $(docker images -q)'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph --decorate'
alias gco='git checkout'
alias gb='git branch'
EOF

# Create development directories
log "Creating development directory structure..."
mkdir -p /opt/dev/{projects,tools,configs,scripts}

# Install monitoring tools
log "Installing monitoring and performance tools..."
apt-get install -y \
    prometheus \
    grafana \
    netdata

# Setup firewall
log "Configuring firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8080/tcp
ufw allow 3000/tcp
ufw allow 5000/tcp
ufw allow 6443/tcp  # Kubernetes API
ufw allow 10250/tcp # Kubelet API
ufw allow 2379:2380/tcp # etcd
ufw --force enable

# Create helpful scripts
log "Creating utility scripts..."

# Create system info script
cat > /usr/local/bin/devlab-info <<'EOF'
#!/bin/bash
echo "=== Dev Lab System Information ==="
echo "Hostname: $(hostname)"
echo "IP Address: $(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -1)"
echo "Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
echo "Kubernetes: $(kubectl version --client --short 2>/dev/null || echo 'Not installed')"
echo "Python: $(python3 --version)"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "Go: $(go version 2>/dev/null || echo 'Not installed')"
echo "=================================="
EOF
chmod +x /usr/local/bin/devlab-info

# Final setup
log "Performing final setup..."

# Enable SSH
systemctl enable ssh
systemctl start ssh

# Clean up
apt-get autoremove -y
apt-get autoclean

# Display summary
echo -e "${GREEN}"
echo "================================================"
echo "   Dev Lab Setup Complete!                      "
echo "================================================"
echo -e "${NC}"
echo ""
echo "System Configuration:"
echo "  Hostname: $HOSTNAME"
[[ -n "$STATIC_IP" ]] && echo "  IP Address: $STATIC_IP"
echo "  DNS Servers: $DNS1, $DNS2"
echo ""
echo "Installed Components:"
[[ "$INSTALL_DOCKER" =~ ^[Yy]$ ]] && echo "  ✓ Docker & Docker Compose"
[[ "$INSTALL_K8S" =~ ^[Yy]$ ]] && echo "  ✓ Kubernetes (kubectl, minikube, k3s, helm, k9s)"
[[ "$INSTALL_PYTHON" =~ ^[Yy]$ ]] && echo "  ✓ Python Development Tools"
[[ "$INSTALL_NODE" =~ ^[Yy]$ ]] && echo "  ✓ Node.js & npm"
echo "  ✓ Go"
echo "  ✓ Rust"
echo "  ✓ VS Code CLI"
echo "  ✓ GitHub CLI"
echo "  ✓ AgenticScrum Framework"
echo ""
echo "Next Steps:"
echo "  1. Reboot the system: sudo reboot"
echo "  2. Run 'devlab-info' to see system status"
echo "  3. Check AgenticScrum in ~/AgenticScrum"
echo ""
warning "Remember to log out and back in for Docker group membership to take effect!"
echo ""
log "Setup script completed successfully!"