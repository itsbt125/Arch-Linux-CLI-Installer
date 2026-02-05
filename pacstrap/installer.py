import os
import subprocess
import time
import sys

def install_packages(files, extra_pkgs=[]):
    base_pkgs = [
        "linux", "linux-headers", "linux-firmware", "base", "sudo", "nano", 
        "grub", "efibootmgr", "networkmanager", "plasma-nm", 
        "pipewire", "pipewire-alsa", "sddm", "plasma-meta", 
        "konsole", "dolphin", "firefox"
    ]

    custom_pkgs = []
    
    print(f"\n--- DEBUG: Checking Presets ---")
    print(f"Current Working Directory: {os.getcwd()}") # tells you where python is running from
    
    for file_path in files:
        print(f"Looking for: {file_path}")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    # Read lines, strip whitespace, remove empty lines
                    lines = [line.strip() for line in f if line.strip()]
                    
                if lines:
                    print(f"  [OK] Found {len(lines)} packages in {file_path}")
                    custom_pkgs.extend(lines)
                else:
                    print(f"  [WARNING] File exists but is EMPTY: {file_path}")
            except Exception as e:
                print(f"  [ERROR] Could not read file: {e}")
        else:
            print(f"  [ERROR] FILE NOT FOUND at: {os.path.abspath(file_path)}")

    # Combine and Deduplicate (Preserving Order)
    raw_list = base_pkgs + custom_pkgs + extra_pkgs
    full_list = list(dict.fromkeys(raw_list))

    if not full_list:
        print("No packages selected.")
        return

    print(f"\n--- Final Package List ({len(full_list)} total) ---")
    # Print the last 5 packages to verify custom ones are there
    print(f"Tail end of list: {full_list[-10:]}") 

    cmd = ["pacstrap", "-K", "/mnt"] + full_list
    
    print("\nStarting pacstrap...")
    try:
        subprocess.run(cmd, check=True)
        print("\nInstallation complete.")
    except subprocess.CalledProcessError:
        print("\n[ERROR] Pacstrap failed.")
        sys.exit(1)
