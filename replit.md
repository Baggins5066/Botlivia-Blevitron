# Blevitron Discord Bot

## Project Status
✅ **Memory-Driven Bot with User Profiles** - Bot generates personalized responses using conversation database + user profiles (Oct 21, 2025)

### Recent Changes (Oct 21, 2025)
- **✨ NEW: User Profile System** - PostgreSQL database for personalized user information:
  - **User-specific notes** - Store facts, preferences, and context about each Discord user
  - **Profile commands** - Easy-to-use Discord commands for managing profiles (`!addnote`, `!profile`, etc.)
  - **Personalized responses** - Bot uses profile information alongside conversation memories
  - **PostgreSQL storage** - Structured data in `user_profiles` table with notes array and preferences JSON
  - **Profile context injection** - Automatically loaded when responding to each user
  
- **🔄 Memory-Driven Architecture** - Bot synthesizes responses from database memories:
  - **Removed predefined persona/personality** - No hardcoded character traits
  - **Retrieves 40 relevant messages** for comprehensive context
  - **Memories framed as conversation history** - LLM generates responses based on patterns in past messages
  - **Author attribution included** - Each memory shows who said it: `[username]: message`
  - **Broader similarity threshold (0.25)** - Captures more contextually relevant memories
  - **Neutral decision logic** - Bot decides to reply based on engagement heuristics
  - System instruction includes user profile personalization
  
- **ChromaDB Local Storage** - File-based vector database:
  - All message embeddings stored locally in `chroma_data/` directory
  - 636 unique messages with 768-dimensional vectors and author metadata
  - No external database dependencies - fully self-contained project
  - Easy to back up, deploy, and version control
  
- **RAG Memory System** - Vector database with semantic search:
  - ChromaDB for local vector similarity search with cosine distance
  - Google text-embedding-004 for generating 768-dimensional vectors
  - Semantic search retrieves relevant past messages before generating responses
  - Bot has "memory" of 636 unique Discord conversations
  - Easy ingestion pipeline for adding more message history
  
- **Previous improvements**:
  - Fixed mention system using regex word boundaries
  - Added DM handling to prevent crashes
  - Migrated from PostgreSQL to ChromaDB successfully
  
- Configured for VM deployment (always-on background worker)

### Main Components
- **bot.py**: Core bot logic including Discord event handlers, message processing, and profile management commands
- **config.py**: Configuration settings and API keys
- **llm.py**: LLM integration for AI-powered responses with user profile context and comprehensive memory retrieval (40 messages)
- **user_profiles.py**: PostgreSQL database operations for user profile management (CRUD operations)
- **utils.py**: Utility functions for logging and smart user mention handling with regex
- **chromadb_storage.py**: Local vector database storage using ChromaDB with cosine similarity
- **memory_search.py**: Semantic search using vector embeddings, retrieves 40 messages with author attribution
- **message_parser.py**: Parser for Discord export text files to extract message content and author information
- **embedding_pipeline.py**: Pipeline to generate embeddings and store them in ChromaDB
- **migrate_postgres_to_chromadb.py**: One-time migration script from PostgreSQL to ChromaDB
- **requirements.txt**: Python dependencies (discord.py, colorama, aiohttp, chromadb, psycopg2-binary)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests to Gemini API
- `chromadb` (v1.2+): Local vector database for semantic similarity search
- `psycopg2-binary`: PostgreSQL database adapter for user profiles

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `LLM_API_KEY`: Google Gemini API key for embeddings and responses
- `DATABASE_URL`: PostgreSQL connection string (automatically provided by Replit)

### Prerequisites
1. Set up the required API keys as environment variables:
   - `DISCORD_BOT_TOKEN`: Get from [Discord Developer Portal](https://discord.com/developers/applications)
   - `LLM_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Running the Bot
The bot runs automatically via the "Discord Bot" workflow. It will:
1. Validate that API keys are set
2. Connect to Discord
3. Load local ChromaDB vector database from `chroma_data/` directory
4. Connect to PostgreSQL database for user profiles
5. When responding, retrieve:
   - User profile information (if available)
   - 40 relevant memories from past conversations (with author attribution)
6. Generate personalized responses using both profile data and conversation patterns

### Adding More Training Data
To add more Discord message history to the bot's memory:
1. Place Discord export `.txt` files in the `attached_assets/` folder
2. Run: `python embedding_pipeline.py`
3. The script will automatically:
   - Parse messages from all .txt files
   - Generate embeddings using Google's API
   - Store them in ChromaDB (stored in `chroma_data/` directory)
   - Skip any duplicate messages automatically
4. Bot will immediately have access to the new memories

### Data Storage
- **ChromaDB (Local)**: All conversation embeddings stored in `chroma_data/` directory with author metadata
  - Portable - entire database is part of the project
  - Automatic hash-based deduplication
  - By default, `chroma_data/` is committed to git
- **PostgreSQL (User Profiles)**: Structured user information stored in database
  - User profiles with notes array and preferences JSON
  - Persistent across deployments
  - Supports complex queries and relationships

### Managing User Profiles
Use Discord commands to manage user information:

**View a profile:**
```
!profile @username
!profile  (view your own profile)
```

**Add a note to a user:**
```
!addnote @Baggins Loves discussing philosophy and AI
```

**Set all notes for a user:**
```
!setnotes @Baggins Enjoys deep conversations | Friend since 2023 | Prefers thoughtful responses
```

**List all profiles:**
```
!profiles
```

**Get help:**
```
!help
```

Notes are used to personalize responses - the bot will consider this information when interacting with each user.

### Deployment
The bot is configured for **Reserved VM (Background Worker)** deployment:
- **Deployment Type**: VM (always-on background worker)
- **Run Command**: `python bot.py`
- This configuration is appropriate for Discord bots that need to maintain persistent connections

## User Preferences
None documented yet.

## Security Notes
- API keys are stored as environment variables, not in code
- .gitignore configured to prevent committing sensitive files
- Bot tokens should never be shared or committed to version control
