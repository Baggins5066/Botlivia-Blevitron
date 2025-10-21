"""
User profile management module using local JSON file storage.
Stores and retrieves personalized information about Discord users.
"""

import json
import os
from typing import Optional, List, Dict, Any
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
    notes: Optional[List[str]] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Create or update a user profile.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        notes: List of notes about the user
        preferences: User preferences dictionary
    
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
                profiles[user_key]['notes'] = notes or []
                profiles[user_key]['preferences'] = preferences or {}
                profiles[user_key]['updated_at'] = now
            else:
                # Create new profile
                profiles[user_key] = {
                    'discord_id': discord_id,
                    'username': username,
                    'notes': notes or [],
                    'preferences': preferences or {},
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


def add_note_to_user(discord_id: int, username: str, note: str) -> bool:
    """
    Add a note to a user's profile.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        note: Note text to add
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If note is empty or only whitespace
    """
    if not note or not note.strip():
        raise ValueError("Note cannot be empty")
    
    try:
        with file_lock:
            profiles = _load_profiles()
            user_key = str(discord_id)
            now = datetime.utcnow().isoformat()
            
            if user_key in profiles:
                # Add note to existing profile
                if note not in profiles[user_key]['notes']:
                    profiles[user_key]['notes'].append(note)
                profiles[user_key]['username'] = username
                profiles[user_key]['updated_at'] = now
            else:
                # Create new profile with note
                profiles[user_key] = {
                    'discord_id': discord_id,
                    'username': username,
                    'notes': [note],
                    'preferences': {},
                    'created_at': now,
                    'updated_at': now
                }
            
            _save_profiles(profiles)
            return True
    except Exception as e:
        print(f"Error adding note to user: {e}")
        return False


def set_user_notes(discord_id: int, username: str, notes: List[str]) -> bool:
    """
    Set (replace) all notes for a user.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        notes: List of notes to set
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with file_lock:
            profiles = _load_profiles()
            user_key = str(discord_id)
            now = datetime.utcnow().isoformat()
            
            if user_key in profiles:
                # Update notes on existing profile
                profiles[user_key]['notes'] = notes
                profiles[user_key]['username'] = username
                profiles[user_key]['updated_at'] = now
            else:
                # Create new profile with notes
                profiles[user_key] = {
                    'discord_id': discord_id,
                    'username': username,
                    'notes': notes,
                    'preferences': {},
                    'created_at': now,
                    'updated_at': now
                }
            
            _save_profiles(profiles)
            return True
    except Exception as e:
        print(f"Error setting user notes: {e}")
        return False


def get_all_profiles() -> List[Dict[str, Any]]:
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
    
    if not profile:
        return ""
    
    # Filter out empty notes
    notes = [note for note in profile.get('notes', []) if note and note.strip()]
    
    if not notes:
        return ""
    
    context = f"User Profile for {profile['username']}:\n"
    for note in notes:
        context += f"- {note}\n"
    
    return context
