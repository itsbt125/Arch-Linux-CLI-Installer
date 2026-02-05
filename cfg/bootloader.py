import subprocess
import os
import sys

def install_grub(disk_path):
    print("\nInstalling GRUB...")
    
    # Check if we are actually in UEFI mode (optional safety check)
    if not os.path.exists("/sys/firmware/efi/efivars"):
        print("This system is NOT booted into UEFI mode, aborting install.")
        sys.exit(0)
    try:
        cmd_install = [
            "arch-chroot", "/mnt",
            "grub-install",
            "--target=x86_64-efi",
            "--efi-directory=/boot",
            "--bootloader-id=ArchLinux",
            "--recheck"
        ]
        subprocess.run(cmd_install, check=True)

        cmd_config = [ # Generates grub configuration file
            "arch-chroot", "/mnt",
            "grub-mkconfig",
            "-o", "/boot/grub/grub.cfg"
        ]
        subprocess.run(cmd_config, check=True)
        
        print("GRUB installed successfully.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"GRUB installation failed: {e}")
        return False