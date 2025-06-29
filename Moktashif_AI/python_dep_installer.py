#!/usr/bin/env python3
"""
Moktashif_AI Python Dependencies Installer
Handles common pip installation issues with multiple fallback methods
"""

import subprocess
import sys
import os
import importlib.util

def print_status(message):
    print(f"\033[92m[INFO]\033[0m {message}")

def print_warning(message):
    print(f"\033[93m[WARNING]\033[0m {message}")

def print_error(message):
    print(f"\033[91m[ERROR]\033[0m {message}")

def check_python_env():
    """Check Python environment and pip availability"""
    print_status("Checking Python environment...")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print_status("Running in virtual environment")
        return False  # Don't use --user in venv
    else:
        print_warning("Not in virtual environment, will use --user flag")
        return True

def upgrade_pip():
    """Upgrade pip using multiple methods"""
    print_status("Upgrading pip...")
    
    methods = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user"],
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--break-system-packages"],
    ]
    
    for method in methods:
        try:
            result = subprocess.run(method, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print_status("Pip upgraded successfully")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            continue
    
    print_warning("Could not upgrade pip, continuing with current version")
    return False

def install_package(package_name, use_user=True):
    """Install a Python package with multiple fallback methods"""
    print_status(f"Installing {package_name}...")
    
    # Different installation methods to try
    methods = []
    
    if use_user:
        methods.append([sys.executable, "-m", "pip", "install", package_name, "--user", "--quiet"])
    
    methods.extend([
        [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
        [sys.executable, "-m", "pip", "install", package_name, "--break-system-packages", "--quiet"],
        [sys.executable, "-m", "pip", "install", package_name, "--user", "--break-system-packages", "--quiet"],
        [sys.executable, "-m", "pip", "install", package_name, "--force-reinstall", "--no-deps", "--quiet"],
    ])
    
    for i, method in enumerate(methods):
        try:
            result = subprocess.run(method, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print_status(f"✓ {package_name} installed successfully (method {i+1})")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            continue
    
    print_error(f"✗ Failed to install {package_name}")
    return False

def verify_package(package_name):
    """Verify that a package is properly installed"""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is not None:
            return True
    except ImportError:
        pass
    return False

def install_via_apt(package_name, apt_name):
    """Try to install package via apt (Linux only)"""
    if os.name != 'posix':
        return False
    
    try:
        print_status(f"Trying to install {package_name} via apt as {apt_name}")
        result = subprocess.run(
            ["sudo", "apt-get", "install", "-y", apt_name],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("=" * 50)
    print("Moktashif_AI Python Dependencies Installer")
    print("=" * 50)
    
    # Check environment
    use_user_flag = check_python_env()
    
    # Upgrade pip
    upgrade_pip()
    
    # Define packages to install
    core_packages = {
        'requests': 'python3-requests',
        'beautifulsoup4': 'python3-bs4', 
        'dnspython': 'python3-dnspython',
        'colorama': 'python3-colorama',
    }
    
    optional_packages = {
        'selenium': None,
        'paramiko': None,
        'scapy': None,
        'python-nmap': None,
        'tabulate': None,
    }
    
    # Install core packages
    print_status("Installing core packages...")
    failed_core = []
    
    for package, apt_name in core_packages.items():
        if not install_package(package, use_user_flag):
            if apt_name and install_via_apt(package, apt_name):
                print_status(f"✓ {package} installed via apt")
            else:
                failed_core.append(package)
    
    # Install optional packages
    print_status("Installing optional packages...")
    failed_optional = []
    
    for package, apt_name in optional_packages.items():
        if not install_package(package, use_user_flag):
            failed_optional.append(package)
    
    # Install from requirements.txt if available
    if os.path.exists('requirements.txt'):
        print_status("Installing from requirements.txt...")
        methods = [
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
        ]
        
        if use_user_flag:
            methods.insert(0, [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user", "--quiet"])
        
        for method in methods:
            try:
                result = subprocess.run(method, capture_output=True, text=True, timeout=180)
                if result.returncode == 0:
                    print_status("Requirements.txt installed successfully")
                    break
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                continue
        else:
            print_warning("Could not install all packages from requirements.txt")
    
    # Verify installations
    print_status("Verifying installations...")
    
    all_packages = list(core_packages.keys()) + list(optional_packages.keys())
    working_packages = []
    broken_packages = []
    
    for package in all_packages:
        # Handle special cases
        import_name = package
        if package == 'beautifulsoup4':
            import_name = 'bs4'
        elif package == 'python-nmap':
            import_name = 'nmap'
        
        if verify_package(import_name):
            working_packages.append(package)
            print_status(f"✓ {package} is working")
        else:
            broken_packages.append(package)
            print_error(f"✗ {package} verification failed")
    
    # Summary
    print("\n" + "=" * 50)
    print("INSTALLATION SUMMARY")
    print("=" * 50)
    
    print(f"Working packages ({len(working_packages)}): {', '.join(working_packages)}")
    
    if failed_core:
        print_error(f"Failed core packages ({len(failed_core)}): {', '.join(failed_core)}")
        print_error("These packages are required for Moktashif_AI to work properly!")
    
    if failed_optional:
        print_warning(f"Failed optional packages ({len(failed_optional)}): {', '.join(failed_optional)}")
        print_warning("These packages are optional and won't prevent basic functionality")
    
    if broken_packages:
        print_error(f"Broken packages ({len(broken_packages)}): {', '.join(broken_packages)}")
        print_error("These packages installed but can't be imported")
    
    # Recommendations
    print("\nRECOMMENDations:")
    
    if failed_core or broken_packages:
        print("1. Try creating a virtual environment:")
        print("   python3 -m venv moktashif_venv")
        print("   source moktashif_venv/bin/activate")
        print("   python3 install_python_deps.py")
        print("")
        print("2. Try installing system packages:")
        print("   sudo apt-get update")
        print("   sudo apt-get install python3-pip python3-dev")
        print("   sudo apt-get install python3-requests python3-bs4 python3-dnspython")
        print("")
        print("3. If still failing, try manual installation:")
        for pkg in failed_core:
            print(f"   python3 -m pip install {pkg} --user --force-reinstall")
    else:
        print_status("All packages installed successfully!")
        print_status("You can now run: python main.py --url http://target.com")

if __name__ == "__main__":
    main()
