import subprocess
from cfg.cmds import cmd

VERBOSE = False

def run_chroot(cmd): 
    full_cmd = ["arch-chroot", "/mnt"] + cmd
    try:
        #subprocess.run(full_cmd, check=True)
        cmd(full_cmd)
    except subprocess.CalledProcessError as e:
        print(f"[!] Chroot command failed: {' '.join(cmd)}")
        raise e

def generate_fstab():
    print("[-] Generating fstab...")
    #subprocess.run("genfstab -U /mnt > /mnt/etc/fstab", shell=True, check=True)
    cmd("genfstab -U /mnt > /mnt/etc/fstab",shell=True)
def configure_system(hostname, username, user_password, root_password, timezone="America/New_York", locale="en_US.UTF-8", keymap="us"):
    print(f"[-] Configuring system: {hostname}")
    run_chroot(["ln", "-sf", f"/usr/share/zoneinfo/{timezone}", "/etc/localtime"])
    run_chroot(["hwclock", "--systohc"])
    print(f"[-] Setting console keymap: {keymap}")
    #subprocess.run(f'echo "KEYMAP={keymap}" > /mnt/etc/vconsole.conf',chec=True,shell=True)
    cmd(f'echo "KEYMAP={keymap}" > /mnt/etc/vconsole.conf',shell=True)
    run_chroot(["sed", "-i", f"s/^#{locale}/{locale}/", "/etc/locale.gen"])
    run_chroot(["locale-gen"])
    #subprocess.run(f'echo "LANG={locale}" > /mnt/etc/locale.conf',check=True,shell=True)
    cmd(f'echo "LANG={locale}" > /mnt/etc/locale.conf',shell=True)
    subprocess.run(f'echo "{hostname}" > /mnt/etc/hostname',check=True,shell=True)    
    #subprocess.run(f'echo "127.0.0.1\tlocalhost\n::1\tlocalhost\n127.0.1.1\t{hostname}.localdomain\t{hostname}" > /mnt/etc/hosts', shell=True)    
    print("[-] Configuring Root password...")
    ps = subprocess.Popen(["echo", f"root:{root_password}"], stdout=subprocess.PIPE)
    subprocess.run(["arch-chroot", "/mnt", "chpasswd"], stdin=ps.stdout, check=True)
    ps.stdout.close()

    print(f"[-] Creating user: {username}")
    try:
        run_chroot(["useradd", "-m", "-G", "wheel,network,video,audio,storage", username])
    except:
        print("[!] Error adding user, might already exist.")
        
    ps_user = subprocess.Popen(["echo", f"{username}:{user_password}"], stdout=subprocess.PIPE)
    subprocess.run(["arch-chroot", "/mnt", "chpasswd"], stdin=ps_user.stdout, check=True)
    ps_user.stdout.close()

    run_chroot(["sed", "-i", "s/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/", "/etc/sudoers"]) # Adds user account to sudoers group
    print("[-] Enabling services...") # Enables NetworkManager and sddm on next boot
    services = ["NetworkManager", "sddm"]
    for s in services:
        run_chroot(["systemctl", "enable", s])
        
    return True