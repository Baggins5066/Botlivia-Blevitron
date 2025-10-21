"""
User profile management module for PostgreSQL database.
Stores and retrieves personalized information about Discord users.
"""

import psycopg2
import psycopg2.extras
import os
from typing import Optional, List, Dict, Any
import json

DATABASE_URL = os.getenv("DATABASE_URL")

# Register JSON adapter for psycopg2
psycopg2.extras.register_default_jsonb()


def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(DATABASE_URL)


def get_user_profile(discord_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user profile by Discord ID.
    
    Args:
        discord_id: Discord user ID
        
    Returns:
        Dictionary with user profile data or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT discord_id, username, notes, preferences, created_at, updated_at
            FROM user_profiles
            WHERE discord_id = %s
        """, (discord_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            # Normalize notes to always be a list
            notes = row[2] if row[2] is not None else []
            # Preferences: psycopg2 returns JSONB as dict already, handle both cases
            preferences = row[3] if row[3] is not None else {}
            if isinstance(preferences, str):
                import json
                try:
                    preferences = json.loads(preferences)
                except:
                    preferences = {}
            elif not isinstance(preferences, dict):
                preferences = {}
            
            return {
                'discord_id': row[0],
                'username': row[1],
                'notes': list(notes) if notes else [],
                'preferences': preferences,
                'created_at': row[4],
                'updated_at': row[5]
            }
        return None
        
    except Exception as e:
        print(f"Error getting user profile: {e}")
        raise


def create_or_update_user_profile(discord_id: int, username: str, notes: Optional[List[str]] = None, 
                                   preferences: Optional[Dict[str, Any]] = None) -> bool:
    """
    Create a new user profile or update existing one.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        notes: List of notes/facts about the user
        preferences: Dictionary of user preferences
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        notes = notes or []
        preferences = preferences or {}
        
        # Wrap preferences dict in Json adapter for JSONB
        cursor.execute("""
            INSERT INTO user_profiles (discord_id, username, notes, preferences)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (discord_id) 
            DO UPDATE SET 
                username = EXCLUDED.username,
                notes = EXCLUDED.notes,
                preferences = EXCLUDED.preferences,
                updated_at = CURRENT_TIMESTAMP
        """, (discord_id, username, notes, psycopg2.extras.Json(preferences)))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating/updating user profile: {e}")
        raise


def add_note_to_user(discord_id: int, username: str, note: str) -> bool:
    """
    Add a note to a user's profile. Creates profile if it doesn't exist.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        note: Note to add
        
    Returns:
        True if successful, False otherwise
    """
    if not note or not note.strip():
        raise ValueError("Note cannot be empty")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First ensure the user exists with proper array initialization
        cursor.execute("""
            INSERT INTO user_profiles (discord_id, username, notes)
            VALUES (%s, %s, ARRAY[]::text[])
            ON CONFLICT (discord_id) DO NOTHING
        """, (discord_id, username))
        
        # Then append the note
        cursor.execute("""
            UPDATE user_profiles
            SET notes = array_append(COALESCE(notes, ARRAY[]::text[]), %s),
                updated_at = CURRENT_TIMESTAMP
            WHERE discord_id = %s
        """, (note.strip(), discord_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding note to user: {e}")
        raise


def set_user_notes(discord_id: int, username: str, notes: List[str]) -> bool:
    """
    Replace all notes for a user. Creates profile if it doesn't exist.
    
    Args:
        discord_id: Discord user ID
        username: Discord username
        notes: List of notes to set (empty list allowed to clear notes)
        
    Returns:
        True if successful, False otherwise
    """
    # Filter out empty/whitespace notes
    filtered_notes = [n.strip() for n in notes if n and n.strip()]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_profiles (discord_id, username, notes)
            VALUES (%s, %s, %s)
            ON CONFLICT (discord_id) 
            DO UPDATE SET 
                notes = EXCLUDED.notes,
                updated_at = CURRENT_TIMESTAMP
        """, (discord_id, username, filtered_notes))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error setting user notes: {e}")
        raise


def delete_user_profile(discord_id: int) -> bool:
    """
    Delete a user profile.
    
    Args:
        discord_id: Discord user ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM user_profiles WHERE discord_id = %s", (discord_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error deleting user profile: {e}")
        return False


def get_all_profiles() -> List[Dict[str, Any]]:
    """
    Get all user profiles.
    
    Returns:
        List of user profile dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT discord_id, username, notes, preferences, created_at, updated_at
            FROM user_profiles
            ORDER BY username
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        profiles = []
        for row in rows:
            # Normalize notes to always be a list
            notes = row[2] if row[2] is not None else []
            # Preferences: psycopg2 returns JSONB as dict already, handle both cases
            preferences = row[3] if row[3] is not None else {}
            if isinstance(preferences, str):
                import json
                try:
                    preferences = json.loads(preferences)
                except:
                    preferences = {}
            elif not isinstance(preferences, dict):
                preferences = {}
            
            profiles.append({
                'discord_id': row[0],
                'username': row[1],
                'notes': list(notes) if notes else [],
                'preferences': preferences,
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        return profiles
        
    except Exception as e:
        print(f"Error getting all profiles: {e}")
        raise


def format_profile_context(discord_id: int) -> str:
    """
    Format user profile as context string for LLM.
    
    Args:
        discord_id: Discord user ID
        
    Returns:
        Formatted string with user profile information, or empty string if no profile
    """
    profile = get_user_profile(discord_id)
    
    if not profile or not profile['notes']:
        return ""
    
    # Filter out empty/whitespace notes
    valid_notes = [note.strip() for note in profile['notes'] if note and note.strip()]
    
    if not valid_notes:
        return ""
    
    notes_text = "\n".join([f"- {note}" for note in valid_notes])
    
    context = f"""[USER PROFILE - {profile['username']}]:
{notes_text}
"""
    
    return context
