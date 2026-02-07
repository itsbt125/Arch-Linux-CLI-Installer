import os
import subprocess
import time
import sys

def enable_multilib(conf_path):
    sed_snip = r'/^# *\[multilib\]/,/^# *Include/ s/^# *//'
    try:
        subprocess.run(["sed", "-i", sed_snip, conf_path], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_packages(files, extra_pkgs):
    base_pkgs = ["linux", "linux-headers", "linux-firmware", "base", "sudo", 
                 "nano", "grub", "efibootmgr", "networkmanager", "plasma-nm", 
                 "pipewire", "pipewire-alsa", "sddm", "plasma-meta", 
                 "konsole", "dolphin", "firefox"]
    
    custom_pkgs = []
    for file in files:
        if os.path.exists(file):
            with open(file, "r") as f:
                custom_pkgs.extend(f.read().splitlines())

    full_list = list(set(base_pkgs + [p.strip() for p in custom_pkgs if p.strip()] + extra_pkgs))

    if not full_list:
        print("No packages selected.")
        return

    print(f"Preparing to install {len(full_list)} packages...")

    if enable_multilib("/etc/pacman.conf"):
        subprocess.run(["pacman", "-Sy"], check=True)
    else:
        print("Warning: Failed to enable multilib on host.")

    try:
        subprocess.run(["pacstrap", "-K", "/mnt", "base"], check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)

    if not enable_multilib("/mnt/etc/pacman.conf"):
         print("Error enabling multilib on target system.")
         sys.exit(1)

    task_start = time.time()
    try:
        subprocess.run(["pacstrap", "-K", "/mnt"] + full_list, check=True)
        print("Packages have completed installation.")
    except subprocess.CalledProcessError:
        print("Error installing packages.")
        sys.exit(1)

    print(f"Total time: {time.time() - task_start:.2f} seconds")
