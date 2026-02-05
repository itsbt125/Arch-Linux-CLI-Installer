#disks.py

import subprocess
import json
import sys
import time

def get_disks():
    result = subprocess.run(["lsblk", "-dno", "NAME,SIZE,MODEL", "--json"], capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    # Return list of disks (ignoring loop devices)
    return [f"/dev/{d['name']} - {d['model']} ({d['size']})" 
            for d in data.get('blockdevices', []) 
            if not d['name'].startswith('loop')]

def prepare_drive(disk_path, use_swap=False):
    print(f"PREPARING {disk_path}...")

    layout = "label: gpt\nsize=1G, type=U\n" # Partition 1: EFI/Boot 
    if use_swap:
        swap_size = input("Do you want to use a swap with a size other than 4G? (if yes enter the amount of G you want with no units/ if no just press enter)")
        if swap_size:
            layout += f"size={swap_size}G, type=S\n"
        else:
            print("Using swap size of 4G.")
            layout += "size=4G, type=S\n" # Partition 2: Swap (Optional)

    layout += "size=+, type=L\n" # Partition 2 or 3 (Last partion is always root with the rest of the space allocated towards it)

    # Apply the layout
    subprocess.run(["sfdisk", disk_path], input=layout, text=True, check=True)
    subprocess.run(["partprobe", disk_path], check=True)
    time.sleep(1) # Waiting is typically good practice

    # Formatting - Figure out names (/dev/sda1 vs /dev/nvme0n1p1)
    sep = ""
    if "nvme" in disk_path:
        sep = "p"
    p_boot = f"{disk_path}{sep}1"
    
    if use_swap:
        p_swap = f"{disk_path}{sep}2"
        p_root = f"{disk_path}{sep}3"
    else:
        p_root = f"{disk_path}{sep}2"

    print(f"Formatting Boot: {p_boot}")
    subprocess.run(["mkfs.fat", "-F32", p_boot], check=True)

    if use_swap:
        print(f"Formatting Swap: {p_swap}")
        subprocess.run(["mkswap", p_swap], check=True)
        subprocess.run(["swapon", p_swap], check=True)

    print(f"ormatting Root: {p_root}")
    subprocess.run(["mkfs.ext4", "-F", p_root], check=True)

    print(f"Mounting {p_root} to /mnt")
    subprocess.run(["mount", p_root, "/mnt"], check=True)
    
    subprocess.run(["mkdir", "-p", "/mnt/boot"], check=True)
    subprocess.run(["mount", p_boot, "/mnt/boot"], check=True)

    return True

if __name__ == "__main__":
    disks = get_disks()
    if not disks:
        print("No disks found...")
        sys.exit()

    for i, d in enumerate(disks):
        print(f"[{i}] {d}")

    try:
        index = int(input("\nSelect Disk Index: "))
        target_disk = disks[index].split(" - ")[0] # Extract just the path (e.g., "/dev/sda") from the string
    except:
        print("Invalid selection.")
        sys.exit()

    swap_choice = input("Add swap partition? (y/n): ").lower() == 'y'
    if input(f"\nWIPE {target_disk}? Type 'YES': ") != "YES":
        sys.exit()

    prepare_drive(target_disk, swap_choice)
    print("\nDrive is mounted and ready.")