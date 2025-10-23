import json
import re
from typing import Dict, Any

class UserProfile:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserProfile, cls).__new__(cls)
            cls._instance.users = {}
            cls._instance.aliases = {}
            cls._instance.load_users()
        return cls._instance

    def load_users(self):
        try:
            with open('users.json', 'r') as f:
                self.users = json.load(f)
                self.build_alias_map()
        except FileNotFoundError:
            self.users = {}

    def build_alias_map(self):
        self.aliases = {}
        for user_id, user_data in self.users.items():
            # Add username to aliases
            username = user_data.get('username', '').lower()
            if username:
                self.aliases[username] = user_data['username']

            # Add aliases from the 'aliases' field
            for alias in user_data.get('aliases', []):
                self.aliases[alias.lower()] = user_data['username']

    def get_all_users(self) -> Dict[str, Any]:
        return self.users

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        return self.users.get(user_id)

def replace_aliases_with_usernames(text: str) -> str:
    user_profile = UserProfile()

    # Generate a regex pattern from the alias map keys
    # Sort by length descending to match longer aliases first
    sorted_aliases = sorted(user_profile.aliases.keys(), key=len, reverse=True)
    pattern = '|'.join(re.escape(alias) for alias in sorted_aliases)

    if not pattern:
        return text

    def replacer(match):
        matched_alias = match.group(0).lower()
        return user_profile.aliases.get(matched_alias, match.group(0))

    return re.sub(pattern, replacer, text, flags=re.IGNORECASE)

if __name__ == '__main__':
    # Test cases

    # Mock users.json for testing
    mock_users = {
        "123": {"username": "Baggins", "aliases": ["Aiden"]},
        "456": {"username": "snazzydaddy", "aliases": ["Snazzy Daddy", "Miles"]}
    }
    with open('users.json', 'w') as f:
        json.dump(mock_users, f)

    # Test the replacement function
    test_text = "Hey Snazzy Daddy, how are you? Aiden is also here."
    processed_text = replace_aliases_with_usernames(test_text)

    print(f"Original: {test_text}")
    print(f"Processed: {processed_text}")

    # Clean up mock file
    import os
    os.remove('users.json')