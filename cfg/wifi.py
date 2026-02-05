import subprocess
import time
import sys
import re

def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running command: {e}")
        return ""

def get_wireless_device():
    """Finds the name of the wireless device (e.g., wlan0)"""
    output = run_command(["iwctl", "device", "list"])
    
    for line in output.split('\n'):
        if "station" in line:
            parts = line.split()
            if len(parts) > 0:
                return re.sub(r'\x1b\[[0-9;]*m', '', parts[0])
    
    return "wlan0"

def get_wifi_networks(device):
    print(f"Scanning for networks on {device}...")
    
    subprocess.run(["iwctl", "station", device, "scan"], stdout=subprocess.DEVNULL)
    time.sleep(3) # Wait for results
    
    output = run_command(["iwctl", "station", device, "get-networks"])
    
    networks = []
    lines = output.split('\n')
    
    for line in lines:
        clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
        security = "Open"

        if "psk" in clean_line: security = "WPA/WPA2"
        elif "8021x" in clean_line: security = "Enterprise"
        elif "wep" in clean_line: security = "WEP"
        
        parts = re.split(r'\s{2,}', clean_line)
        
        if len(parts) >= 2:
            ssid = parts[0]
            if "Name" in ssid or "----" in ssid:
                continue
                
            active = ">" in line
            ssid = ssid.replace(">", "").strip()
            
            if ssid:
                networks.append({
                    "ssid": ssid,
                    "security": security,
                    "active": active
                })

    return networks

def connect_to_wifi():
    device = get_wireless_device()
    print(f"Detected Wireless Device: {device}")
    
    while True:
        networks = get_wifi_networks(device)
        
        if not networks:
            print("No networks found. (Is the switch on?)")
            if input("Retry? (y/n): ").lower() != 'y':
                return False
            continue

        print("\nWi-Fi Network Selection")
        for i, net in enumerate(networks):
            mark = "*" if net['active'] else " "
            print(f"[{i}] {mark} {net['ssid']} ({net['security']})")
            
        print("[R] Rescan")
        print("[S] Skip")
        
        choice = input("Select: ").lower()
        if choice == 's': return False
        if choice == 'r': continue
        
        try:
            target = networks[int(choice)]
        except:
            print("Invalid index.")
            continue

        print(f"Connecting to {target['ssid']}...")
        
        cmd = ["iwctl", "station", device, "connect", target['ssid']]
        
        if "Open" not in target['security']:
            password = input(f"Password for {target['ssid']}: ")
            cmd = ["iwctl", "--passphrase", password, "station", device, "connect", target['ssid']]
        
        try:
            subprocess.run(cmd, check=True)
            print("Connection command sent. Verifying...")
            time.sleep(3)
            
            # Verify internet
            ping = subprocess.run(["ping", "-c", "1", "archlinux.org"], stdout=subprocess.DEVNULL)
            if ping.returncode == 0:
                print("[SUCCESS] Connected!")
                return True
            else:
                print("[WARNING] Connected to router, but no internet.")
                return True # Technically connected
        except subprocess.CalledProcessError:
            print("[ERROR] Connection failed.")
