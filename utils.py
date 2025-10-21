import datetime
from colorama import Fore, Style, init
from config import BAGGINS_ID, SNAZZYDADDY_ID

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
            .replace(f"<@{BAGGINS_ID}>", f"<@{BAGGINS_ID}>")
            .replace(f"<@{SNAZZYDADDY_ID}>", f"<@{SNAZZYDADDY_ID}>")
    )