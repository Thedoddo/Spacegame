#!/usr/bin/env python3
"""
Build script to create an executable for the Galactic Conquest game.
"""

import os
import subprocess
import sys

def build_exe():
    """Build the executable using PyInstaller"""
    
    print("Building Galactic Conquest executable...")
    
    # PyInstaller command with options
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # Hide console window (for GUI apps)
        "--name=GalacticConquest",      # Name of the executable
        "--icon=icon.ico",              # Icon file (if you have one)
        "--add-data=game;game",         # Include the game folder
        "--hidden-import=pygame",       # Ensure pygame is included
        "--hidden-import=random",       # Ensure random is included
        "--hidden-import=math",         # Ensure math is included
        "--hidden-import=sys",          # Ensure sys is included
        "--hidden-import=os",           # Ensure os is included
        "main.py"                       # Main script
    ]
    
    # Remove icon option if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
        print("Note: No icon.ico found, building without custom icon")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created: dist/GalacticConquest.exe")
        print("\nYou can now run the game by double-clicking GalacticConquest.exe in the 'dist' folder")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def build_exe_simple():
    """Simple build without advanced options"""
    print("Building with simple options...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=GalacticConquest",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("Simple build successful!")
        print(f"Executable created: dist/GalacticConquest.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Simple build failed: {e}")
        return False

if __name__ == "__main__":
    print("Galactic Conquest - Executable Builder")
    print("=" * 40)
    
    # Try advanced build first, fall back to simple if it fails
    if not build_exe():
        print("\nAdvanced build failed, trying simple build...")
        build_exe_simple() 