import subprocess
import json
import sys
import time

def get_disks():
    result = subprocess.run(["lsblk", "-dno", "NAME,SIZE,MODEL", "--json"], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return [f"/dev/{d['name']} - {d['model']} ({d['size']})" 
            for d in data.get('blockdevices', []) 
            if not d['name'].startswith('loop')]

def prepare_drive(disk_path, use_swap=False, swap_size="4"):
    print(f"[-] Preparing {disk_path}...")
    layout = "label: gpt\nsize=1G, type=U\n" 
    if use_swap:
        print(f"Adding swap partition: {swap_size}G")
        layout += f"size={swap_size}G, type=S\n"
    layout += "size=+, type=L\n" 
    try:
        subprocess.run(["sfdisk", disk_path], input=layout, text=True, check=True)
        subprocess.run(["partprobe", disk_path], check=True)
    except subprocess.CalledProcessError:
        print("[!] Partitioning failed!")
        return False

    sep = "p" if "nvme" in disk_path else ""
    p_boot = f"{disk_path}{sep}1"
    if use_swap:
        p_swap = f"{disk_path}{sep}2"
        p_root = f"{disk_path}{sep}3"
    else:
        p_root = f"{disk_path}{sep}2"

    print(f"[-] Formatting boot: {p_boot}")
    subprocess.run(["mkfs.fat", "-F32", p_boot], check=True)

    if use_swap:
        print(f"[-] Formatting swap: {p_swap}")
        subprocess.run(["mkswap", p_swap], check=True)
        subprocess.run(["swapon", p_swap], check=True)

    print(f"[-] Formatting root: {p_root}")
    subprocess.run(["mkfs.ext4", "-F", p_root], check=True)
    print(f"[-] Mounting {p_root} to /mnt")
    subprocess.run(["mount", p_root, "/mnt"], check=True)
    subprocess.run(["mkdir", "-p", "/mnt/boot"], check=True)
    subprocess.run(["mount", p_boot, "/mnt/boot"], check=True)

    return True
