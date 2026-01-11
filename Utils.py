import os
import sys
import platform
import logging
import re

# paths for log folder. 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "soc_ip_triage.log")


def setup_logging():
    # create log folder if it does not exist
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    logging.info("Program started")

#cheking if os is compatible
def check_os():
    os_name = platform.system()
    supported_os = ["Windows", "Linux", "Darwin"]

    if os_name not in supported_os:
        print("Unsupported operating system")
        logging.error(f"Unsupported OS: {os_name}")
        sys.exit(1)

    logging.info(f"OS check passed: {os_name}")

#cheking if user has log premission 
def check_log_permissions():
    try:
        with open(LOG_FILE, "a"):
            pass
        logging.info("Log file permission OK")
    except IOError:
        print("Cannot write to log file")
        sys.exit(1)

#Defines Ip regex. Validating IPv4 addresses with regex. 
def is_valid_ipv4(ip):
    # basic IPv4 regex
    pattern = r"^(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}$"
    return re.match(pattern, ip) is not None

