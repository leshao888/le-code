"""Launcher script to open new terminal window."""

import subprocess
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Command to run
command = f'cd /d "{script_dir}" && python main.py'

# Try to open in new window using different methods
try:
    # Method 1: Using start command (should open new CMD window)
    print("Attempting to open new terminal window...")
    subprocess.Popen(
        ['cmd', '/c', 'start', 'cmd', '/k', command],
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("New terminal window should be opening...")
    print("Please check for the new CMD window.")

except Exception as e:
    print(f"Error: {e}")
    print("\nPlease manually run:")
    print(f'   cd "{script_dir}"')
    print("   python main.py")
