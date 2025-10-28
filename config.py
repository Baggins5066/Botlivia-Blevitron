
import os
import json

# -------- BOT CONFIG --------
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
LLM_API_KEY = os.environ.get("LLM_API_KEY")

# -------- USER IDS --------
def load_user_ids():
    """Load user IDs from users.json"""
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        # Create a mapping of usernames to discord IDs
        user_map = {}
        for discord_id, user_data in users.items():
            username = user_data['username'].lower()
            user_map[username] = discord_id
        
        return user_map
    except Exception as e:
        print(f"Error loading users.json: {e}")
        return {}

# Load user IDs from users.json
_user_ids = load_user_ids()

# Map usernames to their Discord IDs
BAGGINS_ID = _user_ids.get('bagginscord', '')
SNAZZYDADDY_ID = _user_ids.get('snazzydaddy', '')
PHROGSLEG_ID = _user_ids.get('phrogsleg', '')
CORN_ID = _user_ids.get('corn', '')
PUGMONKEY_ID = _user_ids.get('pugmonkey', '')
MEATBRO_ID = _user_ids.get('meatbro', '')  # Not in users.json, will be empty
RESTORT_ID = _user_ids.get('restort', '')
TBL_ID = _user_ids.get('tbl', '')
EVAN_ID = _user_ids.get('even', '')  # Username is "Even" in users.json
DROID_ID = _user_ids.get('droid', '')
