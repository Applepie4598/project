import datetime
import getpass
import logging
import json
import os
import re

from firewall import is_ip_blocked_in_firewall

# Example allowed/block lists (can be loaded from a live IP data folder)
ALLOWED_IPS = {
    "8.8.8.8",
    "1.1.1.1"
}

#Case-sensitive, folders name is "Data" not "data" in the catalog, I suspect this can be the case why it's not reading the IP-files in the catalog 

#Looking in the live_ip_folder name "Data"
def load_blocked_ips(live_ip_folder="Data"):
    """

    Reads all IPs from the live IP folder and returns a set of blocked IPs.
    """
    blocked_ips = set()

    if not os.path.exists(live_ip_folder):
        logging.warning(f"Live IP folder '{live_ip_folder}' not found")
        return blocked_ips

    for file in os.listdir(live_ip_folder):
        file_path = os.path.join(live_ip_folder, file)
        if not os.path.isfile(file_path):
            continue

        with open(file_path, "r") as f:
            for line in f:
                ip = line.strip()
                if is_valid_ipv4(ip):
                    blocked_ips.add(ip)

    return blocked_ips


#IP validation "Regex"
def is_valid_ipv4(ip):
    pattern = r"^(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}$"
    return re.match(pattern, ip) is not None

#looking on the Ip, in blocked list 
def triage_ip(ip, blocked_ips):
    logging.info(f"Checking IP: {ip}")

    # Check if IP is blocked in firewall
    is_blocked_in_firewall = is_ip_blocked_in_firewall(ip)

    # Determine verdict based on firewall status
    if is_blocked_in_firewall:
        verdict = "BLOCKED IN FIREWALL"
    else:
        verdict = "NOT BLOCKED IN FIREWALL"

    # Determine danger level based on threat intelligence data
    if ip in blocked_ips:
        danger_level = "DANGEROUS"
    elif ip in ALLOWED_IPS:
        danger_level = "NOT_DANGEROUS"
    else:
        danger_level = "UNKNOWN"

    result = {
        "ip": ip,
        "verdict": verdict,
        "danger_level": danger_level,
        "checked_at": datetime.datetime.utcnow().isoformat() + "Z",
        "user": getpass.getuser()
    }
#Loggin result 
    logging.info(f"Result: {result}")
    return result

#Write report for ip to json file 
def save_report(result):
    filename = f"report_{result['ip']}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=4)

#Looking through Data folder to match ip if bad. 
def scan_folder_for_bad_ips(folder_to_scan="data", live_ip_folder="data"):
    """
    Scan a folder (folder_to_scan) for IPs and check them against live IP data (live_ip_folder)
    """
    blocked_ips = load_blocked_ips(live_ip_folder)
#cheking if path exist 
    if not os.path.exists(folder_to_scan):
        print(f"Folder '{folder_to_scan}' does not exist")
        logging.error(f"Missing folder: {folder_to_scan}")
        return
#Joins all the ip together
    for file in os.listdir(folder_to_scan):
        file_path = os.path.join(folder_to_scan, file)
        if not os.path.isfile(file_path):
            continue

        logging.info(f"Scanning file: {file_path}")
        #Cheking if Ip is valid and prints result dangerlevel 
        with open(file_path, "r") as f:
            for line in f:
                ip = line.strip()
                if not ip:
                    continue
                if not is_valid_ipv4(ip):
                    logging.warning(f"Invalid IP skipped: {ip}")
                    continue

                result = triage_ip(ip, blocked_ips)
                save_report(result)

                if result["danger_level"] == "DANGEROUS":
                    print(f"[!] BAD IP FOUND: {ip}")
                else:
                    print(f"[OK] {ip}")

