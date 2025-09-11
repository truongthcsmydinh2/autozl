#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for creating executable
Script để đóng gói ứng dụng thành .exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_exe():
    """Build executable using PyInstaller"""
    
    print("🚀 Building Android Automation GUI executable...")
    
    # Get current directory
    current_dir = Path(__file__).parent
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=AndroidAutomationGUI",  # Executable name
        "--icon=assets/icon.ico",       # Application icon (if exists)
        "--add-data=config;config",     # Include config folder
        "--add-data=flows;flows",       # Include flows folder
        "--add-data=assets;assets",     # Include assets folder
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=core.device_manager",
        "--hidden-import=core.flow_manager",
        "--hidden-import=core.config_manager",
        "--clean",                      # Clean cache
        "main_gui.py"                   # Main script
    ]
    
    try:
        # Run PyInstaller
        print("📦 Running PyInstaller...")
        result = subprocess.run(cmd, cwd=current_dir, check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print(f"📁 Executable created in: {current_dir / 'dist'}")
        
        # Show build info
        exe_path = current_dir / "dist" / "AndroidAutomationGUI.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📊 Executable size: {size_mb:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def clean_build():
    """Clean build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    current_dir = Path(__file__).parent
    
    # Directories to clean
    clean_dirs = ["build", "dist", "__pycache__"]
    
    for dir_name in clean_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"🗑️  Removed {dir_path}")
    
    # Remove .spec file
    spec_file = current_dir / "AndroidAutomationGUI.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"🗑️  Removed {spec_file}")
    
    print("✅ Cleanup completed!")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_gui.txt"], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main build function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Android Automation GUI executable")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    parser.add_argument("--build", action="store_true", help="Build executable")
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
    
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    if args.build:
        if not build_exe():
            sys.exit(1)
    
    # If no arguments, do full build
    if not any([args.clean, args.install_deps, args.build]):
        print("🔧 Starting full build process...")
        
        # Install dependencies
        if not install_dependencies():
            sys.exit(1)
        
        # Clean previous builds
        clean_build()
        
        # Build executable
        if not build_exe():
            sys.exit(1)
        
        print("🎉 Build process completed successfully!")
        print("📁 Check the 'dist' folder for your executable.")

if __name__ == "__main__":
    main()