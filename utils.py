import datetime
import re
from colorama import Fore, Style, init
from config import BAGGINS_ID, SNAZZYDADDY_ID, PHROGSLEG_ID, CORN_ID, PUGMONKEY_ID, MEATBRO_ID, RESTORT_ID, TBL_ID, EVAN_ID, DROID_ID
from log_config import logger

# Initialize Colorama
init(autoreset=True)

# -------- Logger with Timestamps --------
def log(message, color=Fore.WHITE):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")
    logger.info(message)

# -------- Replace with Mentions --------
def replace_with_mentions(text):
    """Replace username mentions with Discord mentions using word boundaries to avoid partial matches"""
    
    # Define replacements as (pattern, mention) tuples
    # Using word boundaries (\b) to match whole words only
    replacements = [
        # Baggins
        (r'\bBaggins\b', f'<@{BAGGINS_ID}>'),
        
        # Snazzy Daddy variations
        (r'\bSnazzy Daddy\b', f'<@{SNAZZYDADDY_ID}>'),
        (r'\bSnazzyDaddy\b', f'<@{SNAZZYDADDY_ID}>'),
        (r'\bsnazzydaddy\b', f'<@{SNAZZYDADDY_ID}>'),
        
        # Phrogsleg / Liv variations (match whole words only)
        (r'\bliv!', f'<@{PHROGSLEG_ID}>'),  # No trailing \b after punctuation
        (r'\bliv\b', f'<@{PHROGSLEG_ID}>'),
        (r'\bphrogsleg\b', f'<@{PHROGSLEG_ID}>'),
        (r'\bphrogs leg\b', f'<@{PHROGSLEG_ID}>'),
        
        # Corn variations
        (r'\bcorn\b', f'<@{CORN_ID}>'),
        (r'\bCorn\b', f'<@{CORN_ID}>'),
        (r'\bicy_waterfall\b', f'<@{CORN_ID}>'),
        
        # Ellie / Pugmonkey
        (r'\bEllie\b', f'<@{PUGMONKEY_ID}>'),
        (r'\bellie\b', f'<@{PUGMONKEY_ID}>'),
        (r'\bPugmonkey\b', f'<@{PUGMONKEY_ID}>'),
        (r'\bpugmonkey\b', f'<@{PUGMONKEY_ID}>'),
        
        # Meatbro
        (r'\bmeatbro\b', f'<@{MEATBRO_ID}>'),
        (r'\bMeatbro\b', f'<@{MEATBRO_ID}>'),
        
        # Restort
        (r'\brestort\b', f'<@{RESTORT_ID}>'),
        (r'\bRestort\b', f'<@{RESTORT_ID}>'),
        
        # TBL variations
        (r'\btbl drizzy\b', f'<@{TBL_ID}>'),
        (r'\btbl7133\b', f'<@{TBL_ID}>'),
        (r'\btbl\b', f'<@{TBL_ID}>'),
        (r'\bTbl\b', f'<@{TBL_ID}>'),
        
        # Evan
        (r'\bevanslmd\b', f'<@{EVAN_ID}>'),
        (r'\bevan\b', f'<@{EVAN_ID}>'),
        (r'\bEvan\b', f'<@{EVAN_ID}>'),
        
        # Droid
        (r'\bdroid_7\b', f'<@{DROID_ID}>'),
        (r'\bdroid\b', f'<@{DROID_ID}>'),
        (r'\bDroid\b', f'<@{DROID_ID}>'),
    ]
    
    # Apply each replacement using regex with case-insensitive flag where appropriate
    for pattern, mention in replacements:
        text = re.sub(pattern, mention, text, flags=re.IGNORECASE if pattern.islower() else 0)
    
    return text