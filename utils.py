import datetime
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

# -------- Logger with Timestamps --------
def log(message, color=Fore.WHITE):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")
