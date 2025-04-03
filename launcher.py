#!/usr/bin/env python3
"""
Launcher script for LinkedIn Automation Tool
This script helps verify dependencies and launch the application
"""

import sys
import subprocess
import os
import platform

def check_dependencies():
    """Check if required packages are installed"""
    try:
        # Check Python version
        python_version = sys.version_info
        print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
            print("Warning: This application requires Python 3.6 or higher")
            
        # Try importing tkinter
        print("Checking for Tkinter...")
        import tkinter as tk
        print(f"Tkinter version: {tk.TkVersion}")
        
        # Check if selenium is installed
        print("Checking for Selenium...")
        try:
            import selenium
            print(f"Selenium version: {selenium.__version__}")
        except ImportError:
            print("Selenium not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
            
        # Check if webdriver-manager is installed
        print("Checking for webdriver-manager...")
        try:
            import webdriver_manager
            print(f"webdriver-manager found")
        except ImportError:
            print("webdriver-manager not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
            
        return True
        
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return False

def install_tkinter():
    """Provide instructions for installing tkinter based on OS"""
    system = platform.system().lower()
    
    print("\nTkinter is required but not found. Installation instructions:")
    
    if "linux" in system:
        print("\nFor Debian/Ubuntu:")
        print("  sudo apt-get update")
        print("  sudo apt-get install python3-tk")
        print("\nFor Fedora:")
        print("  sudo dnf install python3-tkinter")
        print("\nFor Arch Linux:")
        print("  sudo pacman -S tk")
    elif "darwin" in system:  # macOS
        print("\nFor macOS:")
        print("  brew install python-tk")
        print("  or download the official Python installer from python.org which includes tkinter")
    elif "windows" in system:
        print("\nFor Windows:")
        print("  - Download and reinstall Python from python.org")
        print("  - During installation, ensure 'tcl/tk and IDLE' is checked")
    else:
        print("Please search for instructions to install tkinter for your operating system")

def main():
    """Main function to launch the application"""
    print("LinkedIn Automation Tool Launcher")
    print("--------------------------------")
    
    try:
        # Check for tkinter specifically first
        import tkinter
    except ImportError:
        print("Error: Tkinter is not installed.")
        install_tkinter()
        input("Press Enter to exit...")
        return
        
    if check_dependencies():
        print("\nAll dependencies satisfied. Starting application...\n")
        try:
            from main import main as start_app
            start_app()
        except Exception as e:
            print(f"Error launching application: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")
    else:
        print("\nFailed to verify all dependencies.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()