import platform
import subprocess
import logging

#Checking for OS 
def get_os_type():
    """Get the operating system type"""
    os_name = platform.system()
    return os_name

#define if ip is blocked in windows firewall
def is_ip_blocked_windows(ip):
    """Check if IP is blocked in Windows Firewall"""
    try:
        rule_name = "SOC_Block_" + ip

        # Check if rule exists via command "netsh advfirewall firewall show rule SOC_BLOCK_IPADDRESS"
        command = ["netsh", "advfirewall", "firewall", "show", "rule", "name=" + rule_name]
        result = subprocess.run(command, capture_output=True, text=True)

        # If rule exists, the output will contain the rule name
        if rule_name in result.stdout:
            return True
        return False
    
    #If error logging in "DATA LOGS"
    except Exception as e:
        logging.error("Error checking Windows firewall: " + str(e))
        return False

#Defines Linux Iptables command "Sudo,Iptables -L, INPUT,-V, -N"
def is_ip_blocked_linux(ip):
    """Check if IP is blocked in Linux iptables"""
    try:
        # List all iptables rules
        command = ["sudo", "iptables", "-L", "INPUT", "-v", "-n"]
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if IP is in the output
        if ip in result.stdout:
            return True
        return False

    except Exception as e:
        logging.error("Error checking Linux iptables: " + str(e))
        return False

#Defines Ip block on mac command "Sudo,pfctl, -t, blocklist, -T, Show"
def is_ip_blocked_mac(ip):
    """Check if IP is blocked in macOS pfctl"""
    try:
        # Check pfctl table
        command = ["sudo", "pfctl", "-t", "blocklist", "-T", "show"]
        result = subprocess.run(command, capture_output=True, text=True)
#Checking stdout true or false. 
        if ip in result.stdout:
            return True
        return False

    except Exception as e:
        logging.error("Error checking macOS firewall: " + str(e))
        return False

#Cheking type of OS, if Windows,Mac,Darwin. 
def is_ip_blocked_in_firewall(ip):
    """Check if IP is blocked in firewall based on OS"""
    os_type = get_os_type()

    #Check if os is windows
    if os_type == "Windows":
        return is_ip_blocked_windows(ip)
    #Check if os is linux
    elif os_type == "Linux":
        return is_ip_blocked_linux(ip)
    #Check if os is mac
    elif os_type == "Darwin":
        return is_ip_blocked_mac(ip)
    
    else:
        return False


def block_ip_windows(ip):
    """Block an IP address on Windows using Windows Firewall"""
    try:
        rule_name = "SOC_Block_" + ip
        
        # Command to block IP in Windows Firewall
        command = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=" + rule_name,
            "dir=in",
            "action=block",
            "remoteip=" + ip
        ]
        
        print("\n[*] Blocking IP on Windows Firewall...")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Successfully blocked IP:", ip)
            logging.info("Blocked IP in Windows Firewall: " + ip)
            return True
        else:
            print("[!] Failed to block IP")
            print("Error:", result.stderr)
            logging.error("Failed to block IP in Windows Firewall: " + ip)
            return False
            
    except Exception as e:
        print("[!] Error blocking IP:", str(e))
        logging.error("Error blocking IP: " + str(e))
        return False


def block_ip_linux(ip):
    """Block an IP address on Linux using iptables"""
    try:
        # Command to block IP using iptables
        command = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
        
        print("\n[*] Blocking IP on Linux iptables...")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Successfully blocked IP:", ip)
            logging.info("Blocked IP in Linux iptables: " + ip)
            return True
        else:
            print("[!] Failed to block IP")
            print("Error:", result.stderr)
            logging.error("Failed to block IP in Linux iptables: " + ip)
            return False
            
    except Exception as e:
        print("[!] Error blocking IP:", str(e))
        logging.error("Error blocking IP: " + str(e))
        return False


def block_ip_mac(ip):
    """Block an IP address on macOS using pfctl"""
    try:
        # Add IP to pf firewall table
        command = ["sudo", "pfctl", "-t", "blocklist", "-T", "add", ip]
        
        print("\n[*] Blocking IP on macOS firewall...")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Successfully blocked IP:", ip)
            logging.info("Blocked IP in macOS firewall: " + ip)
            return True
        else:
            print("[!] Failed to block IP")
            print("Error:", result.stderr)
            logging.error("Failed to block IP in macOS firewall: " + ip)
            return False
            
    except Exception as e:
        print("[!] Error blocking IP:", str(e))
        logging.error("Error blocking IP: " + str(e))
        return False


def block_ip_in_firewall(ip):
    """Block an IP address in the firewall based on OS"""
    os_type = get_os_type()
    
    print("\n" + "=" * 50)
    print("FIREWALL BLOCKING")
    print("=" * 50)
    print("Operating System:", os_type)
    print("IP to block:", ip)
    
    if os_type == "Windows":
        print("\nNote: You may need to run this program as Administrator")
        return block_ip_windows(ip)
    
    elif os_type == "Linux":
        print("\nNote: You need sudo privileges to block IPs")
        return block_ip_linux(ip)
    
    elif os_type == "Darwin":
        print("\nNote: You need sudo privileges to block IPs")
        return block_ip_mac(ip)
    
    else:
        print("[!] Unsupported operating system:", os_type)
        logging.error("Unsupported OS for firewall blocking: " + os_type)
        return False


def ask_to_block_ip(ip):
    """Ask user if they want to block the IP in firewall"""
    print("\n" + "=" * 50)
    answer = input("Do you want to block this IP in your firewall? (yes/no): ")
    answer = answer.strip().lower()
    
    if answer == "yes" or answer == "y":
        return block_ip_in_firewall(ip)
    else:
        print("[*] IP not blocked in firewall")
        return False

