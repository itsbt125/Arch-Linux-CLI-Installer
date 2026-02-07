import subprocess

def run_chroot(cmd): 
    full_cmd = ["arch-chroot", "/mnt"] + cmd
    try:
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Chroot command failed: {' '.join(cmd)}")
        raise e

def generate_fstab():
    print("[-] Generating fstab...")
    with open("/mnt/etc/fstab", "w") as f:
        subprocess.run(["genfstab", "-U", "/mnt"], stdout=f, check=True)

def configure_system(hostname, username, user_password, root_password, timezone="America/New_York", locale="en_US.UTF-8", keymap="us"):
    print(f"[-] Configuring System: {hostname}")

    run_chroot(["ln", "-sf", f"/usr/share/zoneinfo/{timezone}", "/etc/localtime"])
    run_chroot(["hwclock", "--systohc"])
    print(f"[-] Setting Console Keymap: {keymap}")
    with open("/mnt/etc/vconsole.conf", "w") as f:
        f.write(f"KEYMAP={keymap}\n")

    run_chroot(["sed", "-i", f"s/^#{locale}/{locale}/", "/etc/locale.gen"])
    run_chroot(["locale-gen"])
    
    with open("/mnt/etc/locale.conf", "w") as f:
        f.write(f"LANG={locale}\n")

    with open("/mnt/etc/hostname", "w") as f:
        f.write(f"{hostname}\n")
    
    with open("/mnt/etc/hosts", "w") as f:
        f.write(f"127.0.0.1\tlocalhost\n::1\t\tlocalhost\n127.0.1.1\t{hostname}.localdomain\t{hostname}\n")

    print("[-] Configuring Root Password...")
    ps = subprocess.Popen(["echo", f"root:{root_password}"], stdout=subprocess.PIPE)
    subprocess.run(["arch-chroot", "/mnt", "chpasswd"], stdin=ps.stdout, check=True)
    ps.stdout.close()

    print(f"[-] Creating User: {username}")
    try:
        run_chroot(["useradd", "-m", "-G", "wheel,network,video,audio,storage", username])
    except:
        print("[!] User might already exist.")
        
    ps_user = subprocess.Popen(["echo", f"{username}:{user_password}"], stdout=subprocess.PIPE)
    subprocess.run(["arch-chroot", "/mnt", "chpasswd"], stdin=ps_user.stdout, check=True)
    ps_user.stdout.close()

    run_chroot(["sed", "-i", "s/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/", "/etc/sudoers"]) # Adds user account to sudoers group

    print("[-] Enabling Services...") # Enables NetworkManager and sddm on next boot
    services = ["NetworkManager", "sddm"]
    for s in services:
        run_chroot(["systemctl", "enable", s])

    return True
