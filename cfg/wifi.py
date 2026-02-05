import subprocess
import time
import sys

def run_command(cmd):
    """Run a shell command and return the output string."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_wifi_networks():
    """Scans for networks and returns a list of dictionaries."""
    print("Scanning for Wi-Fi networks... (this takes 3 seconds)")
    
    run_command(["nmcli", "device", "wifi", "rescan"])
    time.sleep(3)
    
    output = run_command(["nmcli", "-t", "-f", "IN-USE,SSID,BARS,SECURITY", "device", "wifi", "list"])
    
    if not output:
        return []

    networks = []
    seen_ssids = set()

    for line in output.split('\n'):
        parts = line.split(':')
        
        if len(parts) < 4:
            continue
            
        in_use = parts[0] == "*"
        ssid = parts[1]
        bars = parts[2]
        security = parts[3]

        # Filter out empty SSIDs and duplicates
        if ssid and ssid not in seen_ssids:
            seen_ssids.add(ssid)
            networks.append({
                "ssid": ssid,
                "bars": bars,
                "security": security,
                "active": in_use
            })
    
    return networks

def connect_to_wifi():
    """Main menu logic."""
    while True:
        networks = get_wifi_networks()
        
        if not networks:
            print("No Wi-Fi networks found.")
            choice = input("Press Enter to scan again, or 's' to skip Wi-Fi setup: ")
            if choice.lower() == 's':
                return False
            continue

        print("\n-Network Selection")
        for i, net in enumerate(networks):
            # Show a * if connected currently
            status = "*" if net['active'] else " "
            print(f"[{i}] {status} {net['ssid']} ({net['bars']}) [{net['security']}]")
        
        print("\n[R] Rescan")
        print("[S] Skip / I am using Ethernet")
        
        choice = input("Select Network: ").lower()
        
        if choice == 's':
            return True # Assume user is skipping because they have ethernet
        if choice == 'r':
            continue

        try:
            idx = int(choice)
            target = networks[idx]
        except (ValueError, IndexError):
            print("Invalid selection.")
            continue

        # Connect
        print(f"\nConnecting to {target['ssid']}...")
        
        # Check if it has security
        if target['security'] == "":
            # Open network
            cmd = ["nmcli", "device", "wifi", "connect", target['ssid']]
        else:
            # Encrypted
            password = input(f"Password for {target['ssid']}: ")
            cmd = ["nmcli", "device", "wifi", "connect", target['ssid'], "password", password]
        
        result = run_command(cmd)
        
        if result:
            print(f"[SUCCESS] Connected to {target['ssid']}!")
            time.sleep(2)
            return True
        else:
            print("[ERROR] Failed to connect. Wrong password?")
            time.sleep(2)


