import sys
import os
import subprocess
import time
sys.path.append(os.getcwd())
from storage import disks
from pacstrap import installer
from cfg import config
from cfg import bootloader
from cfg import drivers
from cfg import wifi 

def check_internet():
    try:
        subprocess.run(["ping", "-c", "1", "archlinux.org"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_valid_options(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return set(result.stdout.strip().splitlines())
    except subprocess.CalledProcessError:
        return set()

def select_from_list(prompt, command, default_val):  # I decided to do this as down the road I'm probably going to have a bunch of lists I need to select from
    valid_options = get_valid_options(command)
    
    print(f"\n{prompt} Selection")
    print(f"Current Default: {default_val}")
    choice = input("Do you want to change this? (y/N): ").lower()
    
    if choice != 'y':
        return default_val

    while True:
        search = input(f"Search {prompt} (e.g. 'New_York' or 'us'): ")
        
        # Filter options based on search
        matches = [opt for opt in valid_options if search.lower() in opt.lower()]
        
        if not matches:
            print("No matches found. Try again.")
            continue
            
        if len(matches) < 20:
            for opt in matches:
                print(f" - {opt}")
        else:
            print(f"Found {len(matches)} matches. Be more specific.")
            continue
            
        selection = input(f"Enter exact {prompt}: ")
        if selection in valid_options:
            return selection
        print("Invalid selection (case-sensitive). Try again.")

def start_install():
    print("Welcome to the Arch Linux installer!")

    # Network Connection Test
    if not check_internet():
        print("[!] No internet connection.")
        if not wifi.connect_to_wifi():
            print("Aborting: Internet required.")
            return

    # Disk Selection
    available = disks.get_disks()
    if not available:
        print("No disks found.")
        return

    for i, d in enumerate(available):
        print(f"[{i}] {d}")
        
    try:
        idx = int(input("\nSelect Disk Index: "))
        target = available[idx].split(" - ")[0]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    # Swap Configuration
    use_swap = input("Use Swap? (y/n): ").lower() == 'y'
    swap_size = "4"
    if use_swap:
        val = input("Swap size in GB (default 4): ")
        if val.strip():
            swap_size = val

    # Hostname & Username/Password (also for root account)
    hostname = input("Hostname: ")
    username = input("Username: ")
    password = input("Password (used for root & user): ")
    
    # Timezone Selection
    timezone = select_from_list(
        "Timezone", 
        ["timedatectl", "list-timezones"], 
        "America/New_York"
    )
    
    # Keyboard Keymap
    keymap = select_from_list(
        "Keymap", 
        ["localectl", "list-keymaps"], 
        "us"
    )

    preset_map = {
        "1": "presets/casual.txt",
        "2": "presets/gaming.txt",
        "3": "presets/development.txt"
    }
    
    selected_presets = []
    
    while True:
        print("\nSelect Presets (Add as many as you want):")
        print("[1] Casual")
        print("[2] Gaming")
        print("[3] Development")
        print("[4] Done / Skip")
        print(f"Current Selection: {[p.split('/')[-1] for p in selected_presets]}")
        
        choice = input("Add Option: ")
        
        if choice == "4":
            break
        elif choice in preset_map:
            path = preset_map[choice]
            if path not in selected_presets:
                selected_presets.append(path)
                print("Added.")
            else:
                print("Already selected.")
        else:
            print("Invalid option.")

    print(f"\nWARNING: WIPING {target}")
    print(f"Presets: {[p.split('/')[-1] for p in selected_presets]}")
    print(f"Timezone: {timezone} | Keymap: {keymap}")
    
    if input("\nType 'YES' to confirm install: ") != "YES":
        return
    
    start_time = time.time()

    # Start of install process
    # Partition & Format drive(s)
    if not disks.prepare_drive(target, use_swap, swap_size):
        return

    # Install Packages (Base + User Presets + Drivers)
    drivers_list = drivers.cpu_microcode_packages() + drivers.gpu_driver_packages()
    installer.install_packages(selected_presets, extra_pkgs=drivers_list)
    
    # Configuration
    config.generate_fstab()
    config.configure_system(
        hostname, 
        username, 
        password, 
        password, 
        timezone, 
        "en_US.UTF-8", 
        keymap
    )
    
    # Install GRUB as the system's bootloader
    bootloader.install_grub(target)
    
    # Exit the environment
    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] Installed in {elapsed:.2f} seconds.")
    print("Rebooting in 5 seconds...")
    time.sleep(5)
    subprocess.run(["reboot", "now"])

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Please run this script as root!")
    else:
        start_install()
