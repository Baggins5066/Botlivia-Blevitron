"""
Initialize the user_profiles table in PostgreSQL.
Run this script once to ensure the database schema exists.
"""

import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def init_user_profiles_table():
    """Create user_profiles table if it doesn't exist."""
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create table with proper schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                discord_id BIGINT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                notes TEXT[] DEFAULT ARRAY[]::TEXT[],
                preferences JSONB DEFAULT '{}'::JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profiles_username 
            ON user_profiles(username);
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ user_profiles table initialized successfully")
        return True
        
    except Exception as e:
        print(f"ERROR initializing user_profiles table: {e}")
        return False


if __name__ == "__main__":
    init_user_profiles_table()
