#installer.py
import os
import subprocess
import time
import sys

def install_packages(files,extra_pkgs):
    base_pkgs = ["linux", "linux-headers", "linux-firmware", "base","sudo", "nano", "grub", "efibootmgr","networkmanager", "plasma-nm", "pipewire", "pipewire-alsa","sddm", "plasma-meta", "konsole", "dolphin", "firefox"] # Required packages
    custom_pkgs = []
    for file in files:
        if os.path.exists(file):
            with open(file, "r") as f:
                custom_pkgs.extend(f.read().splitlines())
                
    full_list = list(set(base_pkgs + [p.strip() for p in custom_pkgs if p.strip()] + extra_pkgs))

    if not full_list:
        print("No packages selected.")
        return

    print(f"Starting install of {len(full_list)} packages.")
    
    # Example: pacstrap -K /mnt pkg1 pkg2 pkg3 ...
    cmd = ["pacstrap", "-K", "/mnt"] + full_list
    task_start = time.time()
    
    try:
        subprocess.run(cmd, check=True)
        print("\nInstallation complete.")
    except subprocess.CalledProcessError:
        print("\nError installing, pacstrap failed.")
        sys.exit(1)

    print(f"Total time: {time.time() - task_start:.2f} seconds")

if __name__ == "__main__":
        install_packages(["presets/casual.txt", "presets/development.txt", "presets/gaming.txt"])

