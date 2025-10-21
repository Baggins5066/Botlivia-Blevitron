"""
Migration script to export user profiles from PostgreSQL to local JSON file.
Run this once to migrate your existing profile data.
"""

import json
import os
import sys

# Check if psycopg2 is available first
POSTGRES_DRIVER_AVAILABLE = False
try:
    import psycopg2
    POSTGRES_DRIVER_AVAILABLE = True
except ImportError:
    pass

# Import the old PostgreSQL module
POSTGRES_MODULE_AVAILABLE = False
ERROR_MESSAGE = None

if not POSTGRES_DRIVER_AVAILABLE:
    ERROR_MESSAGE = """
❌ PostgreSQL driver (psycopg2) is not installed.

To migrate your data from PostgreSQL to local JSON storage:

1. Install the PostgreSQL driver:
   pip install psycopg2-binary

2. Run this migration script again:
   python migrate_postgres_to_local.py

3. After migration, you can uninstall it:
   pip uninstall psycopg2-binary
"""
else:
    try:
        from user_profiles_postgres_old import get_all_profiles as get_postgres_profiles
        POSTGRES_MODULE_AVAILABLE = True
    except ImportError:
        ERROR_MESSAGE = """
❌ PostgreSQL helper module (user_profiles_postgres_old.py) not found.

This file should exist in your project directory.
If you've deleted it, migration from PostgreSQL is not possible.
"""

# Import the new local storage module
from user_profiles_local import _ensure_data_directory, PROFILES_FILE


def migrate_profiles():
    """Migrate user profiles from PostgreSQL to local JSON file."""
    
    if not POSTGRES_MODULE_AVAILABLE:
        if ERROR_MESSAGE:
            print(ERROR_MESSAGE)
        return False
    
    try:
        # Fetch all profiles from PostgreSQL
        print("📥 Fetching profiles from PostgreSQL...")
        postgres_profiles = get_postgres_profiles()
        
        if not postgres_profiles:
            print("ℹ️  No profiles found in PostgreSQL database.")
            return True
        
        print(f"Found {len(postgres_profiles)} profiles")
        
        # Convert to local storage format
        local_profiles = {}
        for profile in postgres_profiles:
            user_key = str(profile['discord_id'])
            local_profiles[user_key] = {
                'discord_id': profile['discord_id'],
                'username': profile['username'],
                'notes': profile.get('notes', []),
                'preferences': profile.get('preferences', {}),
                'created_at': profile.get('created_at', '').isoformat() if hasattr(profile.get('created_at', ''), 'isoformat') else str(profile.get('created_at', '')),
                'updated_at': profile.get('updated_at', '').isoformat() if hasattr(profile.get('updated_at', ''), 'isoformat') else str(profile.get('updated_at', ''))
            }
        
        # Ensure directory exists
        _ensure_data_directory()
        
        # Save to JSON file
        print(f"💾 Saving profiles to {PROFILES_FILE}...")
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(local_profiles, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully migrated {len(local_profiles)} profiles!")
        print(f"📁 Profiles saved to: {PROFILES_FILE}")
        
        # Display summary
        print("\n📊 Migration Summary:")
        for profile in local_profiles.values():
            notes_count = len(profile['notes'])
            print(f"  - {profile['username']}: {notes_count} note(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL → Local JSON Migration")
    print("=" * 60)
    success = migrate_profiles()
    print("=" * 60)
    if success:
        print("✅ Migration complete!")
        print("\nNext steps:")
        print("1. Test the bot with local storage")
        print("2. Verify all profiles are accessible")
        print("3. Remove PostgreSQL dependencies if everything works")
    else:
        print("❌ Migration failed. Please check errors above.")
