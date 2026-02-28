import subprocess
from cfg.cmds import cmd

def cpu_microcode_packages():
    #print("Detecting CPU model for appropriate microcode package installation.")
    try:
        with open("/proc/cpuinfo","r") as f:
            cpu_info = f.read()
        if "AMD" in cpu_info:
            #print("AMD CPU detected, installing amd-ucode.")
            return["amd-ucode"]
        elif "Intel" in cpu_info:
            #print("Intel CPU detected, installing intel-ucode.")
            return["intel-ucode"]
        else:
            return[]
    except:
        return[]
    
def gpu_driver_packages():
    #print("Detecting GPU model for appropriate driver package installation.")
    drivers = []
    try:
        lspci = cmd(["lspci"], capture_output=True, text=True).stdout.lower()
    except:
        #print("Failed to run lspci, skipping GPU detection.")
        return[]

    if "nvidia" in lspci:
        #print("NVIDIA GPU detected.")
        drivers.extend(["nvidia","nvidia-utils","nvidia-settings"])
    if "amd" in lspci or "radeon" in lspci:
        #print("AMD GPU detected.")
        drivers.extend(["mesa","vulkan-radeon","libva-mesa-driver"])
    # Intel support is NOT added yet.
    #print(f"Requesting {drivers} to be installed.")
    return drivers
    
