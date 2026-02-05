# OwO_Farming_Bot

An automated Discord bot farming tool for the OwO Bot that handles hunting, gem management, and includes captcha detection with notifications.

## Features

- **Automated Farming**: Continuously sends farming commands (`oh`, `ob`, `owo`) to maximize hunting activity
- **Smart Gem Management**: 
  - Detects active gem types from hunt messages
  - Automatically selects and uses the highest gems from inactive types
  - Supports 5 gem types with configurable ranges
- **Captcha Detection**: Monitors for captcha challenges and pauses farming with notifications
- **Configurable Timing**: Easily adjust break times and iteration delays
- **Multi-Platform Notifications**: Sound alerts and system notifications when captcha is detected
- **Infinite Runtime**: Runs continuously (no time limits) suitable for GitHub Actions

## Project Structure

```
bot/
├── src/
│   ├── main.py              # Main bot loop
│   ├── initialization.py    # Configuration and token loading
│   ├── captcha_detect.py    # Captcha detection and handling
│   ├── gem_detect.py        # Gem detection and usage
│   ├── config.json           # Local config (ignored)
├── .github/workflows/
│   └── main.yml             # GitHub Actions workflow
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.11+
- Discord bot token from OwO Bot

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure token & channel**
   
   You'll need your Discord token and target channel info. The bot supports:
   
   - **Local development**: Create `src/config.json` (copy from template)
   - **GitHub Actions**: Use repository secrets/inputs (`DISCORD_TOKEN`, `CHANNEL_ID`, `CHANNEL_URL`)
   
   See the "Running" section below for specific setup instructions.

## Configuration

Edit `src/initialization.py` to adjust timing:

```python
# Time range between iterations (in seconds)
ITERATION_WAIT_MIN = 15
ITERATION_WAIT_MAX = 30

# Time range for short breaks after 30 messages (in seconds)
SHORT_BREAK_MIN = 60
SHORT_BREAK_MAX = 300

# Time range for long breaks after 2 cycles (in seconds)
LONG_BREAK_MIN = 60 * 30      # 30 minutes
LONG_BREAK_MAX = 60 * 60      # 60 minutes
```

### Gem Type Configuration

Gem types are defined in `src/initialization.py`:

```python
GEM_TYPES = {
    "type1": range(51, 58),    # Gem IDs 051-057
    "type2": range(58, 65),    # Gem IDs 058-064
    "type3": range(65, 72),    # Gem IDs 065-071
    "type4": range(72, 79),    # Gem IDs 072-078
    "type5": range(79, 86),    # Gem IDs 079-085
}
```

Modify these ranges if your gem ID ranges change.

## Running

### Local Development

1. **Create local config**
   Copy the template and fill in your token + channel info:
   ```json
   {
     "token": "your_discord_token_here",
     "channel_id": "123456789012345678",
     "channel_url": "https://discord.com/channels/server_id/channel_id"
   }
   ```
   Save it as `src/config.json` (this file is ignored by git).

2. **Run the bot**
   ```bash
   python src/main.py
   ```

   You will be prompted in the terminal to choose whether to use star gems (type5).
   To skip the prompt, set `USE_STAR_GEMS=true|false` in your environment.

3. **Stop the bot**
   - Press `Ctrl+C` in the terminal

### GitHub Actions

1. **Add secrets for token & channel config**
   - Go to your repository settings
   - Navigate to **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Add these secrets:
     - `DISCORD_TOKEN` (your Discord token)
     - `CHANNEL_ID` (target channel ID)
     - `CHANNEL_URL` (full channel URL)

2. **The workflow runs automatically**
   - Triggered every 5 minutes (as configured in `.github/workflows/main.yml`)
   - Each run executes for up to 360 minutes (6 hours)
   - Runs are queued to prevent overlapping

3. **Monitor workflow runs**
   - Go to **Actions** tab in your repository
   - Click on "Run OwO script" workflow
   - View logs for each run

4. **Manual trigger (optional)**
   - In the **Actions** tab, select "Run OwO script"
   - Click **Run workflow**
   - Select the branch and click **Run workflow** again
   - Use the **Use star gems (type5)** input to toggle star gems for that run
   - Optional: override `channel_id` / `channel_url` inputs for that run

### GitHub Actions with Local Config File (Not Recommended)

If you prefer to use `src/config.json` in GitHub Actions, you would need to commit it.

⚠️ **Security Warning**: This exposes your token in the repository history. Using secrets is more secure.

## How It Works

1. **Farming Loop**: Sends `oh`, `ob`, and `owo` commands repeatedly
2. **Gem Detection**: Reads recent Discord messages to find active gem types (e.g., `egem3`, `mgem1`, `rgem4`)
3. **Smart Selection**: Uses the highest gems from inactive types only
4. **Break Management**:
   - Short break (1-5 min) after every 30 messages
   - Long break (30-60 min) after 2 cycles
   - Random delays between iterations to avoid detection
5. **Captcha Handling**: 
   - Detects captcha challenges
   - Plays alert sound (Windows)
   - Shows system notification
   - Pauses farming until captcha is resolved
   - Resumes automatically after timeout

## Gem Detection Format

The bot recognizes active gems from Discord messages like:
```
hunt is empowered by <:egem3:ID> [324/450] <:mgem1:ID> [10/75] <:rgem4:ID> [33/50]
```

Where the format is `<:raritygemN:ID>` representing gem types (e.g., egem3 = type3).

## Troubleshooting

### Token not found
**Local Development:**
- Ensure `src/local_token.txt` exists in the correct location
- Check the file contains your token with no extra whitespace
- Verify the file path: `your_repo/src/local_token.txt`

**GitHub Actions:**
- Go to repository Settings → Secrets and verify `DISCORD_TOKEN` is set
- Ensure the secret value is exactly your Discord token (no quotes or extra spaces)
- Check the workflow file uses `${{ secrets.DISCORD_TOKEN }}` correctly

### Bot doesn't start
- Verify `requirements.txt` dependencies are installed
  ```bash
  pip install -r requirements.txt
  ```
- Check Python version is 3.11 or higher
  ```bash
  python --version
  ```

### Gems not detected
- Check that gem ranges in `GEM_TYPES` match your actual gem IDs
- Verify the Discord message format matches the expected pattern
- Add temporary debug output to see what messages the bot receives

### Captcha keeps triggering
- The delay timings may need adjustment
- Consider increasing `ITERATION_WAIT_MAX` to reduce request frequency
- Verify your token is still valid

### GitHub Actions workflow fails
- Check the **Actions** tab → **Run OwO script** → latest run for error logs
- Verify `DISCORD_TOKEN` secret is properly set
- Ensure `.github/workflows/main.yml` hasn't been modified
- Check if your repository has Actions enabled (Settings → Actions → Allow all actions)

## Dependencies

- `requests` - HTTP library for Discord API calls
- `plyer` - System notifications (optional)
- `winsound` - Windows alert sounds (Windows only)

See `requirements.txt` for specific versions.

## Notes

- This bot is designed for use with the OwO Discord bot farming channel
- Always ensure you have proper permissions to run automated tools
- The bot runs indefinitely; use GitHub Actions for reliable scheduled farming
- Captcha detection is active to prevent account lockouts

## License

This project is provided as-is for educational purposes.

## Support

If you encounter issues:
1. Check the configuration in `src/initialization.py`
2. Verify your Discord token is valid
3. Ensure gem type ranges match your inventory
4. Review Discord message format for gem detection
