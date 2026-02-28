import sys
import os
import subprocess
import time
import getpass
sys.path.append(os.getcwd())
from storage import disks
from pacstrap import installer
from cfg import config
from cfg import bootloader
from cfg import drivers
from cfg import wifi 
from cfg.cmds import cmd
from cfg import settings

def check_internet():
    try:
        #subprocess.run(["ping", "-c", "1", "archlinux.org"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        cmd(["ping","-c","1","archlinux.org"])
        return True
    except subprocess.CalledProcessError:
        return False

def get_valid_options(command):
    try:
        result = cmd(command, check=True, text=True, capture_output=True)        
        return set(result.stdout.strip().splitlines())
    except subprocess.CalledProcessError:   
        return set()

def select_from_list(prompt, command, default_val,type):  # I decided to do this as down the road I'm probably going to have a bunch of lists I need to select from
    valid_options = get_valid_options(command)
    print(f"{prompt}")
    print(f"    [-] Current Default: {default_val}")
    choice = input("        [?] Do you want to change this? (y/n): ").strip().lower()
    
    if choice != 'y':
        return default_val

    while True:
        search = input(f"{prompt}: ")
        
        # Filter options based on search
        matches = [opt for opt in valid_options if search.lower() in opt.lower()]
        
        if not matches:
            print("No matches found. Try again.")
            continue
            
        if len(matches) < 64:
            for opt in matches:
                print(f" - {opt}")
        else:
            print(f"Found {len(matches)} matches. Be more specific.")
            continue
            
        selection = input(f"Enter exact {type}: ")
        if selection in valid_options:
            return selection
        print("Invalid selection (case-sensitive). Try again.")

def start_install():
    print("Welcome to the Arch Linux installer made by @itsbt125 on Github.")

    # Network Connection Test
    if not check_internet():
        print("[!] No internet connection.")
        if not wifi.connect_to_wifi():
            print("[!] Aborting: Internet required.")
            return
        
    # Disk Selection
    available = disks.get_disks()
    if not available:
        print("[!] No disks found.")
        return
    print("[-] Listing installable disks found on device.")
    for i, d in enumerate(available):
        print(f"    [{i}] {d}")
        
    try:
        idx = int(input("       [?] Select disk index for installation: "))
        target = available[idx].split(" - ")[0]
    except (ValueError, IndexError):
        print("[!] Invalid selection, aborting installation.")
        return

    # Swap Configuration
    ask = input("[?] It is recommended to use swap. Would you like to use a swap ? (y/n) ").strip().lower()
    if ask == "y" or ask == "yes":
        use_swap = True
        swap_size = 4
        ask = input("   [?] Would you like your swap to be different than 4GB? (y/n) ").strip().lower()
        if ask == "y" or ask == "yes":
            try:
                swap_size = int(input("        [?] How many GB would you like your swap to be? ").strip())
            except ValueError:
                print("[!] An error occured, aborting installation.")
                return
        print(f"    [-] Using {swap_size}GB swap.")
    else:
        use_swap = False
        swap_size = None
        print("    [-] Not using swap.")
    # Hostname & Username/Password (also for root account)
    hostname = input("[?] Please enter a hostname to be used for network identity: ")
    username = input("[?] Enter username for user account: ")
    password = getpass.getpass(prompt=f"[?] Enter a password for {username}: ")
    password_again = getpass.getpass(prompt=f"[?] Enter the password for {username}, again: ")
    if password != password_again:
        print("[!] Passwords do not match, aborting.")
        return
    root_password = getpass.getpass(prompt=f"[?] Enter new root account password: ")
    password_again = getpass.getpass(prompt=f"[?] Enter new root password, again: ")
    if root_password != password_again:
        print("[!] Passwords do not match, aborting.")
        return
    # Timezone Selection
    timezone = select_from_list("[?] Search for a timezone (e.g. 'America/New_York' or 'CST')", ["timedatectl", "list-timezones"], "America/Los_Angeles","timezone")
    # Keyboard Keymap
    keymap = select_from_list("[?] Select a keymap (e.g. 'us' or 'azerty')", ["localectl", "list-keymaps"], "us","keymap")
    # Package selection
    selected_presets = []
    ask = input("[?] Would you like to have packages pre-installed tailored to your use case? (y/n) ").lower()
    if ask == "y" or ask == "yes":
        ask = input("   [?] Would you like casual-use specific packages (discord, vlc, spotify, etc) to be installed? (y/n) ").lower()
        if ask == "y" or ask == "yes":
            selected_presets.append("pacstrap/presets/casual.txt")
        ask = input("   [?] Would you like programming/development focused packages (git, vim, docker, go, python, gcc, obs-studio, etc) to be installed? (y/n) ").lower()
        if ask == "y" or ask == "yes":
            selected_presets.append("pacstrap/presets/development.txt")
        ask = input("   [?] Would you like gaming focused packages (steam, wine, obs-studio, gamemode, etc) to be installed? (y/n) ").lower()
        if ask == "y" or ask == "yes":
            selected_presets.append("pacstrap/presets/gaming.txt")
    ask = input("[?] Use verbose mode during installation to see details? (y/n)").strip().lower()
    settings.VERBOSE = ask.startswith("y")
    print("[-] The following has been configured with the installer")
    print(f"    [-]  Wiping {target} of all data.")
    print(f"    [-] Packages to download (required packages not shown by installer): {[p.split('/')[-1] for p in selected_presets]}")
    print(f"    [-] Timezone: {timezone}")
    print(f"    [-] Keymap: {keymap}")
    print(f"    [-] Using verbose?: {settings.VERBOSE}")
    
    if input("[?] Type 'YES' to continue with install by starting changes: ") != "YES":
        print("[!] Aborting install, changes have not been made.")
        return
    os.system("clear")
    print("[-] Installation process started.")
    start_time = time.time()

    # Start of install process
    # Partition & Format drive(s)
    print("    [-] Partitioning and formatting drives.")
    if not disks.prepare_drive(target, use_swap, swap_size):
        return

    # Install Packages (Base + User Presets + Drivers)
    #print("    [-] Installing system packages, this can take some time depending on the speed of your internet.")
    drivers_list = drivers.cpu_microcode_packages() + drivers.gpu_driver_packages()
    installer.install_packages(selected_presets, extra_pkgs=drivers_list)
    #print("    [-] Package installation has completed.")

    # Configuration
    #print("    [-] Installation is almost complete, configuring fstab.")
    print("    [-] Generating fstab...")
    config.generate_fstab()
    print("    [-] fstab generated.")
    print("    [-] Writing hostname, accounts, timezones, and keymaps to host.")
    config.configure_system(hostname,username,password,root_password,timezone,"en_US.UTF-8",keymap)
    print("    [-] Writing data to host complete.")
    # Install GRUB as the system's bootloader
    print("    [-] Installing GRUB as system bootloader.")
    bootloader.install_grub(target)
    print("    [-] GRUB successfully installed.")
    # Exit the environment
    elapsed = time.time() - start_time
    print(f"[!] Arch Linux with KDE Plasma successfully installed in {elapsed:.2f} seconds.")
    time.sleep(1)
    input("[-] Press enter to reboot, your Linux journey starts here!")
    cmd(["reboot","now"])
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[!] Please run with elevated permissions.")
    else:
        os.system("clear") # this is a linux installer so we don't need cls btw (lol)
        start_install()
