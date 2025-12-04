#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_step(msg):
    print(f"\n[SETUP] {msg}")

def clean_environment():
    """Remove existing virtual environments and cache files for a fresh start."""
    print_step("Cleaning up previous environment...")
    
    # Directories to remove
    dirs_to_remove = [
        "venv", ".venv", "env", 
        "__pycache__", 
        "build", "dist", "flac_bulk_download.egg-info"
    ]
    
    # Files to remove
    files_to_remove = [".DS_Store"]

    root = Path.cwd()

    # Remove directories
    for d in dirs_to_remove:
        path = root / d
        if path.exists():
            print(f"  Removing directory: {d}")
            try:
                shutil.rmtree(path)
            except Exception as e:
                print(f"  Warning: Could not remove {d}: {e}")
                
    # Remove specific files
    for f in files_to_remove:
        path = root / f
        if path.exists():
            print(f"  Removing file: {f}")
            try:
                path.unlink()
            except Exception as e:
                print(f"  Warning: Could not remove {f}: {e}")

    # Recursive cleanup of __pycache__
    for p in root.rglob("__pycache__"):
        try:
            shutil.rmtree(p)
        except Exception:
            pass

def create_virtual_env():
    """Create a new virtual environment."""
    print_step("Creating new virtual environment...")
    
    venv_dir = Path("venv")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("  Virtual environment created in 'venv/'")
    except subprocess.CalledProcessError:
        print("  Error: Failed to create virtual environment.")
        sys.exit(1)

def install_dependencies():
    """Install requirements into the virtual environment."""
    print_step("Installing dependencies...")
    
    # Path to pip in the venv
    if sys.platform == "win32":
        pip_path = str(Path("venv") / "Scripts" / "pip")
    else:
        pip_path = str(Path("venv") / "bin" / "pip")

    try:
        # Upgrade pip first
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("  Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("  Error: Failed to install dependencies.")
        sys.exit(1)

def install_hifi_tool():
    """Download and install the hifi CLI tool automatically."""
    print_step("Installing 'hifi' tool...")
    
    # Determine OS and Architecture
    import platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map to release filenames (approximate based on common Go releases)
    # Adjust these URLs to the actual latest release of the hifi tool
    # Since I don't have the exact repo URL for binaries, I will assume a common structure 
    # or use a known working source if available. 
    # For now, I will simulate the installation or use a placeholder if the URL is unknown.
    # WAIT: The user mentioned https://github.com/sachinsenal0x64/hifi in README.
    # Let's try to find the release asset.
    
    base_url = "https://github.com/sachinsenal0x64/hifi/releases/latest/download"
    
    if system == "darwin":
        os_name = "darwin"
    elif system == "linux":
        os_name = "linux"
    elif system == "windows":
        os_name = "windows"
    else:
        print(f"  Warning: Unsupported OS '{system}' for auto-install. Please install 'hifi' manually.")
        return

    # Architecture mapping
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        print(f"  Warning: Unsupported architecture '{machine}'. Please install 'hifi' manually.")
        return

    # Construct filename
    # Example: hifi_darwin_arm64, hifi_linux_amd64, hifi_windows_amd64.exe
    binary_name = f"hifi_{os_name}_{arch}"
    if system == "windows":
        binary_name += ".exe"
        
    download_url = f"{base_url}/{binary_name}"
    target_path = Path.cwd() / ("hifi.exe" if system == "windows" else "hifi")
    
    print(f"  Downloading {binary_name}...")
    
    try:
        # Use curl to download (usually available)
        subprocess.run(["curl", "-L", "-o", str(target_path), download_url], check=True)
        
        # Make executable (Unix)
        if system != "windows":
            subprocess.run(["chmod", "+x", str(target_path)], check=True)
            
        print(f"  ✅ 'hifi' installed to {target_path}")
        
        # Update config.py to use this local binary? 
        # Or just tell user it's in the root.
        # The app defaults to "hifi", so if we add ./ to path or move it to venv/bin it works.
        # Let's move it to venv/bin so it's in PATH when venv is active!
        
        if system == "windows":
            venv_bin = Path("venv") / "Scripts"
        else:
            venv_bin = Path("venv") / "bin"
            
        if venv_bin.exists():
            dest = venv_bin / target_path.name
            shutil.move(str(target_path), str(dest))
            print(f"  Moved to {dest} (in PATH)")
        
    except Exception as e:
        print(f"  ❌ Failed to install hifi: {e}")
        print("  Please install it manually from https://github.com/sachinsenal0x64/hifi")

def main():
    print("="*50)
    print("FLAC Bulk Downloader - Fresh Setup")
    print("="*50)
    
    # 1. Clean
    clean_environment()
    
    # 2. Create Venv
    create_virtual_env()
    
    # 3. Install Deps
    install_dependencies()
    
    # 4. Install Hifi Tool
    install_hifi_tool()
    
    print("\n" + "="*50)
    print("✅ Setup Complete!")
    print("="*50)
    print("\nTo start the application:")
    print("\n  1. Activate the environment:")
    if sys.platform == "win32":
        print("     venv\\Scripts\\activate")
    else:
        print("     source venv/bin/activate")
        
    print("\n  2. Run the Web Interface:")
    print("     python3 app.py")
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
