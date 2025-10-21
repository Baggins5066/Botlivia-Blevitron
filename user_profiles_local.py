"""
User profile management module using local JSON file storage.
Stores and retrieves personalized information about Discord users.
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
import threading

PROFILES_DIR = "user_data"
PROFILES_FILE = os.path.join(PROFILES_DIR, "profiles.json")

# Thread lock for file operations
file_lock = threading.Lock()


def _ensure_data_directory():
    """Ensure the user_data directory exists."""
    os.makedirs(PROFILES_DIR, exist_ok=True)


def _load_profiles() -> Dict[str, Any]:
    """Load all profiles from JSON file."""
    _ensure_data_directory()
    
    if not os.path.exists(PROFILES_FILE):
        return {}
    
    try:
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_profiles(profiles: Dict[str, Any]):
    """Save all profiles to JSON file."""
    _ensure_data_directory()
    
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)


def create_or_update_user_profile(
    discord_id: int,
    username: str,
    description: str = ""
) -> bool:
    """
    Create or update a user profile.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        description: Description/persona for how the bot should interact with this user
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with file_lock:
            profiles = _load_profiles()
            
            user_key = str(discord_id)
            now = datetime.utcnow().isoformat()
            
            if user_key in profiles:
                # Update existing profile
                profiles[user_key]['username'] = username
                profiles[user_key]['description'] = description
                profiles[user_key]['updated_at'] = now
            else:
                # Create new profile
                profiles[user_key] = {
                    'discord_id': discord_id,
                    'username': username,
                    'description': description,
                    'created_at': now,
                    'updated_at': now
                }
            
            _save_profiles(profiles)
            return True
    except Exception as e:
        print(f"Error creating/updating user profile: {e}")
        return False


def get_user_profile(discord_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user's profile.
    
    Args:
        discord_id: Discord user ID
    
    Returns:
        Dictionary containing profile data, or None if not found
    """
    try:
        with file_lock:
            profiles = _load_profiles()
            user_key = str(discord_id)
            
            if user_key not in profiles:
                return None
            
            return profiles[user_key]
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        return None


def set_user_description(discord_id: int, username: str, description: str) -> bool:
    """
    Set the description for a user.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        description: Description text
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If description is empty or only whitespace
    """
    if not description or not description.strip():
        raise ValueError("Description cannot be empty")
    
    return create_or_update_user_profile(discord_id, username, description.strip())


def get_all_profiles() -> list[Dict[str, Any]]:
    """
    Retrieve all user profiles.
    
    Returns:
        List of all profile dictionaries
    """
    try:
        with file_lock:
            profiles = _load_profiles()
            return list(profiles.values())
    except Exception as e:
        print(f"Error retrieving all profiles: {e}")
        return []


def format_profile_context(discord_id: int) -> str:
    """
    Format user profile information for LLM context.
    
    Args:
        discord_id: Discord user ID
    
    Returns:
        Formatted string with profile information, or empty string if no profile
    """
    profile = get_user_profile(discord_id)
    
    if not profile or not profile.get('description', '').strip():
        return ""
    
    return f"User Profile for {profile['username']}:\n{profile['description']}\n"
