import subprocess
import os
import sys

def launch_program(exe_path):
    """Safely verifies and launches an external executable file."""

    if not os.path.isfile(exe_path):
        print(f"Error: The file {exe_path} could not be found.")
        return False

    try:
        subprocess.Popen([exe_path])
        print(f"Successfully launched {exe_path}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    target_exe = r"C:\Windows\System32\notepad.exe"

    launch_program(target_exe)