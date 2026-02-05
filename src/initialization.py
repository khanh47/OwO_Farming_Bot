"""
Initialization module - handles token loading and configuration setup
"""
import json
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

def _load_local_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error reading config.json: {e}")
    return {}


_LOCAL_CONFIG = _load_local_config()

# Discord channel configuration (env for Actions, config.json for local)
CHANNEL_ID = os.getenv("CHANNEL_ID") or _LOCAL_CONFIG.get("channel_id")
CHANNEL_URL = os.getenv("CHANNEL_URL") or _LOCAL_CONFIG.get("channel_url")

if not CHANNEL_ID or not CHANNEL_URL:
    print("ERROR: Channel config not found!")
    print("  Option 1 (GitHub Actions): Set CHANNEL_ID and CHANNEL_URL as secrets/inputs")
    print("  Option 2 (Local): Create src/config.json with channel_id and channel_url")
    sys.exit(1)

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
LONG_BREAK_MIN = 60 * 45
LONG_BREAK_MAX = 60 * 80


def load_token():
    """Load Discord token from config.json (local) or environment variable"""
    token = os.getenv("DISCORD_TOKEN")
    if token:
        print("✓ Loaded token from DISCORD_TOKEN environment variable")
        return token.strip()

    token = _LOCAL_CONFIG.get("token") if isinstance(_LOCAL_CONFIG, dict) else None
    if token:
        print("✓ Loaded token from config.json")
        return str(token).strip()

    print("ERROR: Token not found!")
    print("  Option 1 (GitHub Actions): Set DISCORD_TOKEN secret")
    print("  Option 2 (Local): Add token to src/config.json")
    sys.exit(1)


def get_headers(token):
    """Create header dictionary for Discord API requests"""
    return {
        "User-Agent": USER_AGENT,
        "authorization": token,
        "referrer": CHANNEL_URL
    }
