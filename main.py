import sys
import os

# Import your custom modules
# We append paths so Python can find them in subfolders
sys.path.append(os.getcwd())
from storage import disks
from pacstrap import installer
from cfg import config
from cfg import bootloader

def start_install():
    print("=== CUSTOM ARCH INSTALLER ===")
    
    # 1. DISK SELECTION
    available = disks.get_disks()
    if not available:
        print("No disks found!")
        return

    for i, d in enumerate(available):
        print(f"[{i}] {d}")
        
    try:
        idx = int(input("\nSelect Disk: "))
        target = available[idx].split(" - ")[0]
    except:
        print("Invalid selection.")
        return

    # 2. SWAP CONFIG
    use_swap = input("Use Swap? (y/n): ").lower() == 'y'
    swap_size = "4"
    if use_swap:
        val = input("Swap size in GB (default 4): ")
        if val.strip():
            swap_size = val

    # 3. USER CONFIG
    hostname = input("Hostname: ")
    username = input("Username: ")
    password = input("Password (root & user): ")
    
    # 4. PRESETS
    print("\nSelect Preset:")
    print("[1] Casual")
    print("[2] Gaming")
    print("[3] Development")
    preset_choice = input("Choice: ")
    
    preset_map = {
        "1": "presets/casual.txt",
        "2": "presets/gaming.txt",
        "3": "presets/development.txt"
    }
    selected_preset = preset_map.get(preset_choice, "presets/casual.txt")

    # 5. CONFIRMATION
    print(f"\nWARNING: Erasing {target}. Preset: {selected_preset}")
    if input("Type 'YES' to install: ") != "YES":
        return

    # === EXECUTION PHASE ===
    
    # Step A: Partitions
    if not disks.prepare_drive(target, use_swap, swap_size):
        return # Stop if partitioning fails

    # Step B: Packages
    # Note: Ensure the 'presets' folder exists next to main.py!
    installer.install_packages([selected_preset])

    # Step C: Fstab
    config.generate_fstab()

    # Step D: System Config
    # Note: Your config.py takes 5 args: hostname, username, password, timezone, locale
    # We hardcode TZ/Locale for now, or you can ask for them
    config.configure_system(hostname, username, password, "America/New_York", "en_US.UTF-8")

    # Step E: Bootloader
    bootloader.install_grub(target)

    print("\n[DONE] Installation Complete! You can reboot.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Run as root!")
    else:
        start_install()