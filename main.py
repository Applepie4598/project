import logging
import argparse
import json
import os

from Utils import setup_logging, check_os, check_log_permissions, is_valid_ipv4
from triage import triage_ip, save_report, load_blocked_ips
from firewall import ask_to_block_ip

#Cheking input is private ip addresses. 
def is_private_ip(ip):
    """Check if IP is a private/internal IP address"""
    parts = ip.split(".")
    first = int(parts[0])
    second = int(parts[1])

    # 10.0.0.0 - 10.255.255.255
    if first == 10:
        return True

    # 172.16.0.0 - 172.31.255.255
    if first == 172 and 16 <= second <= 31:
        return True

    # 192.168.0.0 - 192.168.255.255
    if first == 192 and second == 168:
        return True

    # 127.0.0.0 - 127.255.255.255 (localhost)
    if first == 127:
        return True

    return False

#Logfile content and logfile name "Logs/soc_ip_triage.log"
def show_log():
    """Show the log file contents"""
    log_file = "logs/soc_ip_triage.log"

    if not os.path.exists(log_file):
        print("[!] Log file not found")
        return
#Visual for us that's why we use \n new line. print "=" 50 times ====
    print("\n" + "=" * 50)
    print("LOG FILE CONTENTS")
    print("=" * 50)
#Log_file r = read f: read content in Log_file
    with open(log_file, "r") as f:
        content = f.read()
        print(content)

    print("=" * 50 + "\n")

#cheking for the ip addresse in the report_file
def show_ip_report(ip):
    """Show the JSON report for a specific IP"""
    report_file = "report_" + ip + ".json"


    if not os.path.exists(report_file):
        print("[!] No report found for IP:", ip)
        return
#Visual  
    print("\n" + "=" * 50)
    print("REPORT FOR IP:", ip)
    print("=" * 50)

    with open(report_file, "r") as f:
        data = json.load(f)
        print(json.dumps(data, indent=4))

    print("=" * 50 + "\n")

#Viaual when it print out it looks good 
def print_result(result):
    """Print the IP check result in a nice format"""
    print("\n" + "=" * 50)
    print("IP Address:", result["ip"])
    print("Verdict:", result["verdict"])
    print("Danger Level:", result["danger_level"])
    print("Checked At:", result["checked_at"])
    print("User:", result["user"])
    print("=" * 50 + "\n")


def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="SOC IP Triage Tool")
    parser.add_argument("-ipv4", help="Check a specific IPv4 address")
    parser.add_argument("-checklog", action="store_true", help="Show the log file")
    parser.add_argument("-checklogip", help="Show JSON report for a specific IP")

    args = parser.parse_args()


    # Setup
    setup_logging()
    check_os()
    check_log_permissions()

    # Handle -checklog argument
    if args.checklog:
        show_log()
        return

    # Handle -checklogip argument
    if args.checklogip:
        show_ip_report(args.checklogip)
        return

    # Load all blocked IPs from data folder
    blocked_ips = load_blocked_ips()

    # Handle -ipv4 argument
    if args.ipv4:
        ip = args.ipv4

        # Check if IP is valid format
        if not is_valid_ipv4(ip):
            print("\n[!] Invalid IPv4 address:", ip)
            print("Valid example: 192.168.1.1")
            print("Each number must be between 0-255\n")
            return

        # Check if IP is private/internal
        if is_private_ip(ip):
            print("\n[!] This is an internal/private IP address")
            print("Internal IPs are not public and cannot be reached from the internet\n")
            return

        # IP is valid and public, so check it
        result = triage_ip(ip, blocked_ips)
        save_report(result)
        print_result(result)

        # Ask if user wants to block this IP in firewall
        # Only ask if IP is dangerous AND not already blocked
        if result["danger_level"] == "DANGEROUS" and result["verdict"] == "NOT BLOCKED IN FIREWALL":
            ask_to_block_ip(ip)

        return

    # No arguments provided - run interactive mode
    print("=" * 50)
    print("SOC IP Triage Tool - Interactive Mode")
    print("=" * 50)
    # More user friendly if the reminder on how to stop the program comes after every user input
    print("Type 'exit' or 'quit' to stop the program\n")

    # Main loop - keep running forever
    while True:
        # Ask user for IP address
        ip = input("Enter IP address to check: ")
        ip = ip.strip()

        # Check if user wants to exit
        if ip == "exit" or ip == "quit" or ip == "q":
            print("\nExiting program. Goodbye!")
            logging.info("Program exited by user")
            break

        # Check if user entered nothing
        if ip == "":
            print("[!] Please enter an IP address\n")
            continue

        # Check if IP is valid format
        if not is_valid_ipv4(ip):
            print("\n[!] Invalid IPv4 address:", ip)
            print("Valid example: 192.168.1.1")
            print("Each number must be between 0-255\n")
            logging.warning("Invalid IP entered: " + ip)
            continue

        # Check if IP is private/internal
        if is_private_ip(ip):
            print("\n[!] This is an internal/private IP address")
            print("Internal IPs are not public and cannot be reached from the internet\n")
            continue

        # IP is valid and public, so check it
        result = triage_ip(ip, blocked_ips)
        save_report(result)
        print_result(result)

        # Ask if user wants to block this IP in firewall
        # Only ask if IP is dangerous AND not already blocked
        if result["danger_level"] == "DANGEROUS" and result["verdict"] == "NOT BLOCKED IN FIREWALL":
            ask_to_block_ip(ip)


if __name__ == "__main__":
    main()







