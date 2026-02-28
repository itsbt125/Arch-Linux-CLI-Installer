import subprocess
import json
import sys
import time
from cfg.cmds import cmd

def get_disks():
    result = cmd(["lsblk", "-dno", "NAME,SIZE,MODEL", "--json"],capture_output=True,text=True)
    #result = subprocess.run(["lsblk", "-dno", "NAME,SIZE,MODEL", "--json"], capture_output=True, text=True)
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
        cmd(["sfdisk", disk_path], text=True, check=True, input=layout)
        #subprocess.run(["sfdisk", disk_path], input=layout, text=True, check=True)
        cmd(["partprobe",disk_path])
        #subprocess.run(["partprobe", disk_path], check=True)
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
    #subprocess.run(["mkfs.fat", "-F32", p_boot], check=True)
    cmd(["mkfs.fat","-F32",p_boot])
    if use_swap:
        print(f"[-] Formatting swap: {p_swap}")
        #subprocess.run(["mkswap", p_swap], check=True)
        cmd(["mkswap",p_swap])
        #subprocess.run(["swapon", p_swap], check=True)
        cmd(["swapon",p_swap])

    print(f"[-] Formatting root: {p_root}")
    #subprocess.run(["mkfs.ext4", "-F", p_root], check=True)
    cmd(["mkfs.ext4", "-F", p_root])
    print(f"[-] Mounting {p_root} to /mnt")
    #subprocess.run(["mount", p_root, "/mnt"], check=True)
    cmd(["mount", p_root, "/mnt"])
    #subprocess.run(["mkdir", "-p", "/mnt/boot"], check=True)
    cmd(["mkdir", "-p", "/mnt/boot"])
    #subprocess.run(["mount", p_boot, "/mnt/boot"], check=True)
    cmd(["mount", p_boot, "/mnt/boot"])

    return True
