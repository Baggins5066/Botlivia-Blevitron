import datetime
from colorama import Fore, Style, init
from config import BAGGINS_ID, SNAZZYDADDY_ID, PHROGSLEG_ID, CORN_ID, PUGMONKEY_ID, MEATBRO_ID, RESTORT_ID, TBL_ID, EVAN_ID, DROID_ID

# Initialize Colorama
init(autoreset=True)

# -------- Logger with Timestamps --------
def log(message, color=Fore.WHITE):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")

# -------- Replace with Mentions --------
def replace_with_mentions(text):
    return (
        text.replace("Baggins", f"<@{BAGGINS_ID}>")
            .replace("Snazzy Daddy", f"<@{SNAZZYDADDY_ID}>")
            .replace("SnazzyDaddy", f"<@{SNAZZYDADDY_ID}>")
            .replace("snazzydaddy", f"<@{SNAZZYDADDY_ID}>")
            .replace(f"<@{SNAZZYDADDY_ID}>", f"<@{SNAZZYDADDY_ID}>")

            .replace("liv", f"<@{PHROGSLEG_ID}>")
            .replace("liv!", f"<@{PHROGSLEG_ID}>")
            .replace("phrogsleg", f"<@{PHROGSLEG_ID}>")
            .replace("phrogs leg", f"<@{PHROGSLEG_ID}>")
            .replace(f"<@{PHROGSLEG_ID}>", f"<@{PHROGSLEG_ID}>")

            .replace("corn", f"<@{CORN_ID}>")
            .replace("Corn", f"<@{CORN_ID}>")
            .replace("icy_waterfall", f"<@{CORN_ID}>")
            .replace(f"<@{CORN_ID}>", f"<@{CORN_ID}>")

            .replace("Ellie", f"<@{PUGMONKEY_ID}>")
            .replace("ellie", f"<@{PUGMONKEY_ID}>")
            .replace("Pugmonkey", f"<@{PUGMONKEY_ID}>")
            .replace("pugmonkey", f"<@{PUGMONKEY_ID}>")
            .replace(f"<@{PUGMONKEY_ID}>", f"<@{PUGMONKEY_ID}>")

            .replace("meatbro", f"<@{MEATBRO_ID}>")
            .replace("Meatbro", f"<@{MEATBRO_ID}>")
            .replace(f"<@{MEATBRO_ID}>", f"<@{MEATBRO_ID}>")
            
            .replace("restort", f"<@{RESTORT_ID}>")
            .replace("Restort", f"<@{RESTORT_ID}>")
            .replace(f"<@{RESTORT_ID}>", f"<@{RESTORT_ID}>")

            .replace("tbl", f"<@{TBL_ID}>")
            .replace("Tbl", f"<@{TBL_ID}>")
            .replace("tbl drizzy", f"<@{TBL_ID}>")
            .replace("tbl7133", f"<@{TBL_ID}>")
            .replace(f"<@{TBL_ID}>", f"<@{TBL_ID}>")

            .replace("evan", f"<@{EVAN_ID}>")
            .replace("Evan", f"<@{EVAN_ID}>")
            .replace("evanslmd", f"<@{EVAN_ID}>")
            .replace(f"<@{EVAN_ID}>", f"<@{EVAN_ID}>")

            .replace("droid", f"<@{DROID_ID}>")
            .replace("Droid", f"<@{DROID_ID}>")
            .replace("droid_7", f"<@{DROID_ID}>")
            .replace(f"<@{DROID_ID}>", f"<@{DROID_ID}>")
    )