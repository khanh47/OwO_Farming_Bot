"""
Initialization module - handles token loading and configuration setup
"""
import os
import sys

# Platform-specific imports
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

# Discord channel configuration
CHANNEL_ID = "1292058301760143392"
CHANNEL_URL = "https://discord.com/channels/1287742668939464736/1292058301760143392"
BASE_URL = f"https://discordapp.com/api/v9/channels/{CHANNEL_ID}/messages"

# Gem type ranges - define which gem IDs belong to which type
GEM_TYPES = {
    "type1": range(51, 58),
    "type2": range(58, 65),
    "type3": range(65, 72),
    "type4": range(72, 79),
    "type5": range(79, 86),
}

# User agent for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36"

# ===== BOT CONFIGURATION =====
# Time range between iterations (in seconds)
ITERATION_WAIT_MIN = 30 
ITERATION_WAIT_MAX = 60 

# Time range for short breaks after 30 messages (in seconds)
SHORT_BREAK_MIN = 60 * 3 
SHORT_BREAK_MAX = 60 * 5

# Time range for long breaks after 2 cycles (in seconds)
LONG_BREAK_MIN = 60 * 45 # 30 minutes
LONG_BREAK_MAX = 60 * 60      # 60 minutes


def load_token():
    """Load Discord token from local_token.txt or environment variable"""
    token = None
    local_token_file = os.path.join(os.path.dirname(__file__), "local_token.txt")
    
    if os.path.exists(local_token_file):
        try:
            with open(local_token_file, "r") as f:
                token = f.read().strip()
            print("✓ Loaded token from local_token.txt")
        except Exception as e:
            print(f"⚠️  Error reading local_token.txt: {e}")
            token = None
    
    # Fall back to environment variable if local token not available
    if not token:
        token = os.getenv("DISCORD_TOKEN")
        if token:
            print("✓ Loaded token from DISCORD_TOKEN environment variable")
    
    if not token:
        print("ERROR: Token not found!")
        print("  Option 1: Create local_token.txt with your Discord token")
        print("  Option 2: Set DISCORD_TOKEN environment variable")
        sys.exit(1)
    
    return token


def get_headers(token):
    """Create header dictionary for Discord API requests"""
    return {
        "User-Agent": USER_AGENT,
        "authorization": token,
        "referrer": CHANNEL_URL
    }
