#!/bin/bash

# Moktashif_AI Dependencies Installation Script
# This script installs required penetration testing tools for the framework

echo "=========================================="
echo "Moktashif_AI Dependencies Installation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
check_privileges() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script needs to be run with sudo privileges"
        print_status "Please run: sudo ./install_dependencies.sh"
        exit 1
    fi
}

# Update package lists
update_packages() {
    print_status "Updating package lists..."
    apt-get update -qq
    if [ $? -eq 0 ]; then
        print_status "Package lists updated successfully"
    else
        print_error "Failed to update package lists"
        exit 1
    fi
}

# Install a package and check if successful
install_package() {
    local package=$1
    print_status "Installing $package..."
    
    if dpkg -l | grep -q "^ii  $package "; then
        print_warning "$package is already installed"
        return 0
    fi
    
    apt-get install -y "$package" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_status "$package installed successfully"
        return 0
    else
        print_error "Failed to install $package"
        return 1
    fi
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install core networking tools
install_core_tools() {
    print_status "Installing core networking tools..."
    
    local core_tools=(
        "curl"
        "wget"
        "netcat-traditional"
        "nmap"
        "jq"
        "python3"
        "python3-pip"
        "git"
        "net-tools"
        "dnsutils"
    )
    
    for tool in "${core_tools[@]}"; do
        install_package "$tool"
    done
    
    # Create netcat symlink if needed
    if ! command_exists nc && command_exists netcat; then
        ln -sf /usr/bin/netcat /usr/bin/nc
        print_status "Created nc symlink for netcat"
    fi
}

# Install penetration testing tools
install_pentest_tools() {
    print_status "Installing penetration testing tools..."
    
    local pentest_tools=(
        "sqlmap"
        "dirb"
        "gobuster"
        "hydra"
        "john"
        "hashcat"
        "nikto"
        "whatweb"
        "sublist3r"
        "wfuzz"
        "ffuf"
    )
    
    for tool in "${pentest_tools[@]}"; do
        if install_package "$tool"; then
            print_status "$tool ready for use"
        else
            print_warning "$tool installation failed, will try alternative methods"
        fi
    done
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip first
    python3 -m pip install --upgrade pip > /dev/null 2>&1
    
    local python_packages=(
        "requests"
        "beautifulsoup4"
        "selenium"
        "paramiko"
        "scapy"
        "dnspython"
        "python-nmap"
        "colorama"
        "tabulate"
    )
    
    for package in "${python_packages[@]}"; do
        print_status "Installing Python package: $package"
        python3 -m pip install "$package" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_status "$package installed successfully"
        else
            print_warning "Failed to install $package"
        fi
    done
}

# Install additional tools from GitHub
install_github_tools() {
    print_status "Installing additional tools from GitHub..."
    
    local temp_dir="/tmp/moktashif_tools"
    mkdir -p "$temp_dir"
    cd "$temp_dir"
    
    # Install SecLists wordlists
    if [ ! -d "/usr/share/seclists" ]; then
        print_status "Installing SecLists wordlists..."
        git clone https://github.com/danielmiessler/SecLists.git > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            mv SecLists /usr/share/seclists
            print_status "SecLists installed to /usr/share/seclists"
        else
            print_warning "Failed to install SecLists"
        fi
    else
        print_warning "SecLists already installed"
    fi
    
    # Install rockyou.txt if not available
    if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
        print_status "Setting up rockyou.txt wordlist..."
        mkdir -p /usr/share/wordlists
        
        if [ -f "/usr/share/wordlists/rockyou.txt.gz" ]; then
            gunzip /usr/share/wordlists/rockyou.txt.gz
            print_status "rockyou.txt extracted"
        else
            print_status "Downloading rockyou.txt..."
            wget -q "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt" -O /usr/share/wordlists/rockyou.txt
            if [ $? -eq 0 ]; then
                print_status "rockyou.txt downloaded"
            else
                print_warning "Failed to download rockyou.txt"
            fi
        fi
    else
        print_warning "rockyou.txt already available"
    fi
    
    # Clean up
    cd /
    rm -rf "$temp_dir"
}

# Verify installations
verify_installations() {
    print_status "Verifying tool installations..."
    
    local tools_to_check=(
        "curl"
        "wget"
        "nc"
        "nmap"
        "jq"
        "python3"
        "sqlmap"
        "dirb"
        "gobuster"
        "hydra"
        "john"
        "nikto"
    )
    
    local failed_tools=()
    
    for tool in "${tools_to_check[@]}"; do
        if command_exists "$tool"; then
            print_status "✓ $tool is available"
        else
            print_error "✗ $tool is not available"
            failed_tools+=("$tool")
        fi
    done
    
    if [ ${#failed_tools[@]} -eq 0 ]; then
        print_status "All tools verified successfully!"
        return 0
    else
        print_error "The following tools failed verification: ${failed_tools[*]}"
        return 1
    fi
}

# Create symbolic links for common tool names
create_symlinks() {
    print_status "Creating symbolic links..."
    
    # Ensure nc points to netcat
    if command_exists netcat && ! command_exists nc; then
        ln -sf $(which netcat) /usr/local/bin/nc
        print_status "Created nc -> netcat symlink"
    fi
    
    # Ensure ffuf is available (install if not present)
    if ! command_exists ffuf; then
        print_status "Installing ffuf from GitHub..."
        wget -q "https://github.com/ffuf/ffuf/releases/latest/download/ffuf_2.1.0_linux_amd64.tar.gz" -O /tmp/ffuf.tar.gz
        tar -xzf /tmp/ffuf.tar.gz -C /tmp/
        mv /tmp/ffuf /usr/local/bin/
        chmod +x /usr/local/bin/ffuf
        rm /tmp/ffuf.tar.gz
        print_status "ffuf installed"
    fi
}

# Fix common permission issues
fix_permissions() {
    print_status "Fixing permissions..."
    
    # Make sure wordlists are readable
    if [ -d "/usr/share/wordlists" ]; then
        chmod -R 644 /usr/share/wordlists/
        print_status "Wordlist permissions fixed"
    fi
    
    if [ -d "/usr/share/seclists" ]; then
        chmod -R 644 /usr/share/seclists/
        print_status "SecLists permissions fixed"
    fi
}

# Main installation process
main() {
    print_status "Starting Moktashif_AI dependencies installation..."
    
    # Check privileges
    check_privileges
    
    # Update packages
    update_packages
    
    # Install tools
    install_core_tools
    install_pentest_tools
    install_python_deps
    install_github_tools
    
    # Post-installation setup
    create_symlinks
    fix_permissions
    
    # Verify everything is working
    if verify_installations; then
        print_status "================================================"
        print_status "Installation completed successfully!"
        print_status "All required tools are now available."
        print_status "You can now run Moktashif_AI without tool issues."
        print_status "================================================"
        
        # Show versions of key tools
        echo ""
        print_status "Installed tool versions:"
        echo "curl: $(curl --version | head -n1)"
        echo "nmap: $(nmap --version | head -n1)"
        echo "sqlmap: $(sqlmap --version 2>/dev/null | head -n1 || echo 'Version check failed')"
        echo "jq: $(jq --version)"
        echo "python3: $(python3 --version)"
        
    else
        print_error "================================================"
        print_error "Installation completed with some failures."
        print_error "Please check the error messages above."
        print_error "You may need to install failed tools manually."
        print_error "================================================"
        exit 1
    fi
}

# Help function
show_help() {
    echo "Moktashif_AI Dependencies Installation Script"
    echo ""
    echo "Usage: sudo ./install_dependencies.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verify   Only verify existing installations"
    echo "  -c, --core     Install only core tools"
    echo ""
    echo "This script installs all required tools for Moktashif_AI including:"
    echo "  - Core networking tools (curl, wget, netcat, nmap, jq)"
    echo "  - Penetration testing tools (sqlmap, dirb, gobuster, hydra, etc.)"
    echo "  - Python dependencies"
    echo "  - Wordlists (SecLists, rockyou.txt)"
    echo ""
}

# Parse command line arguments
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    -v|--verify)
        print_status "Verifying existing installations..."
        verify_installations
        exit $?
        ;;
    -c|--core)
        print_status "Installing core tools only..."
        check_privileges
        update_packages
        install_core_tools
        verify_installations
        exit $?
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac