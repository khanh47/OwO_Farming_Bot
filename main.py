import requests
import time
import random
import re
import winsound
import os

channel_id = "1292058301760143392" 
token = os.getenv("DISCORD_TOKEN")
channel_url = "https://discord.com/channels/1287742668939464736/1292058301760143392"
url = f"https://discordapp.com/api/v9/channels/{channel_id}/messages"

message_count = 0
riel_count = 0
cnt = 0

def check_for_captcha():
    """Check if bot is asking for captcha verification"""
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36",
        "authorization": token,
        "referrer": channel_url
    }
    
    response = requests.get(url + "?limit=5", headers=header)
    if response.status_code == 200:
        messages = response.json()
        for msg in messages:
            content = msg.get('content', '').lower()
            # Check embeds too
            if 'embeds' in msg and msg['embeds']:
                for embed in msg['embeds']:
                    description = embed.get('description', '').lower()
                    title = embed.get('title', '').lower()
                    content += ' ' + description + ' ' + title
            
            # Check for captcha keywords
            captcha_keywords = ['captcha', 'human', 'owobot.com/captcha', 'verify that you are human']
            if any(keyword in content for keyword in captcha_keywords):
                return True
    return False

def notify_captcha():
    """Send notification alert for captcha"""
    # Play alert sound - 3 beeps
    for i in range(3):
        winsound.Beep(1000, 500)  # 1000 Hz for 500ms
        time.sleep(0.3)
    
    # Try to show Windows notification
    try:
        from plyer import notification
        notification.notify(
            title='⚠️ CAPTCHA DETECTED',
            message='OwO Bot requires captcha verification!\nPlease check Discord.',
            app_name='OwO Bot',
            timeout=10
        )
    except ImportError:
        # plyer not installed, just use console output
        print("\n" + "="*50)
        print("⚠️  CAPTCHA ALERT! ⚠️" * 3)
        print("="*50 + "\n")

def wait_for_captcha_resolution(max_wait_minutes=60*24):
    """Wait for captcha to be resolved, then resume
    
    Args:
        max_wait_minutes: Maximum time to wait before resuming anyway (default 30 min)
    """
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    check_interval = 30  # Check every 30 seconds
    
    print(f"\n⏳ PAUSED: Waiting for captcha to be resolved...")
    print(f"Will resume automatically in {max_wait_minutes} minutes if not resolved.")
    print(f"Complete the captcha in Discord to resume immediately.\n")
    
    while True:
        elapsed = time.time() - start_time
        
        # Check if captcha is still there
        if not check_for_captcha():
            elapsed_minutes = int(elapsed // 60)
            elapsed_seconds = int(elapsed % 60)
            print(f"\n✅ CAPTCHA RESOLVED! (waited {elapsed_minutes}m {elapsed_seconds}s)")
            print("Resuming requests...\n")
            break
        
        # Check if max wait time exceeded
        if elapsed >= max_wait_seconds:
            print(f"\n⏱️  TIMEOUT: {max_wait_minutes} minutes reached. Resuming anyway...")
            print("(You may still need to complete the captcha)\n")
            break
        
        # Wait before next check
        remaining = max_wait_seconds - elapsed
        remaining_minutes = int(remaining // 60)
        print(f"Captcha still active... ({remaining_minutes}m remaining) ", end='\r')
        time.sleep(check_interval)

# Gem type ranges - define which gem IDs belong to which type
gem_types = {
    "type1": range(51, 58),    # 051-057
    "type2": range(65, 72),    # 065-071
    "type3": range(72, 79),    # 072-078
    "type4": range(79, 86),    #
}

def get_inventory():
    """Fetch inventory by sending oinv command and reading the response"""
    message = "oinv"
    data = {"content": message}
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36",
        "authorization": token,
        "referrer": channel_url
    }
    
    requests.post(url, json=data, headers=header)
    time.sleep(3)  # Wait longer for bot response
    
    # Get recent messages
    response = requests.get(url + "?limit=15", headers=header)
    if response.status_code == 200:
        messages = response.json()
        for msg in messages:
            # Check message content first
            content = msg.get('content', '')
            if 'Inventory' in content or 'inventory' in content.lower():
                print(f"DEBUG: Found inventory in message content")
                return content
            
            # Check embeds
            if 'embeds' in msg and msg['embeds']:
                for embed in msg['embeds']:
                    title = embed.get('title', '').lower()
                    description = embed.get('description', '')
                    
                    # Check for inventory keywords
                    if ('inventory' in title or 'kurt' in title) and description:
                        print(f"DEBUG: Found inventory embed: {embed.get('title', '')}")
                        return description
    
    print("DEBUG: No inventory found in messages")
    return None

def parse_gems_from_inventory(inventory_text):
    """Parse gem IDs from inventory text"""
    if not inventory_text:
        return []
    
    print(f"DEBUG: Parsing inventory (length: {len(inventory_text)})")
    
    # Find all 3-digit numbers that look like gem IDs (051-126)
    # The format is like: 051 ❤️ 27  or  051 (with emoji and count)
    gems = re.findall(r'\b(0?[0-9]{2,3})\b', inventory_text)
    print(f"DEBUG: Raw numbers found: {gems}")
    
    # Filter to only include gem IDs in our ranges
    valid_gems = []
    for g in gems:
        gem_id = int(g)
        # Check if this gem ID is in any of our defined ranges
        for gem_range in gem_types.values():
            if gem_id in gem_range:
                valid_gems.append(gem_id)
                break
    
    # Remove duplicates and sort
    valid_gems = sorted(list(set(valid_gems)))
    print(f"DEBUG: Valid gems found: {valid_gems}")
    return valid_gems

def get_highest_gems_by_type(available_gems):
    """Get the highest gem ID for each type"""
    selected_gems = []
    
    for gem_type, gem_range in gem_types.items():
        # Find gems of this type
        type_gems = [g for g in available_gems if g in gem_range]
        if type_gems:
            # Get the highest one
            highest = max(type_gems)
            selected_gems.append(highest)
    
    return sorted(selected_gems)[:3]  # Return top 3 gems

def check_active_gems():
    """Check which gem types are currently active by reading recent hunt messages"""
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36",
        "authorization": token,
        "referrer": channel_url
    }
    
    response = requests.get(url + "?limit=15", headers=header)
    if response.status_code == 200:
        messages = response.json()
        for msg in messages:
            if 'embeds' in msg and msg['embeds']:
                embed = msg['embeds'][0]
                description = embed.get('description', '')
                # Check for hunt empowerment text - look for gem emojis and numbers
                if 'hunt is empowered by' in description.lower():
                    # Parse which gems are active - look for numbers in brackets like [75/100]
                    # The gems appear before these brackets
                    lines = description.split('\n')
                    active_gems = []
                    for line in lines:
                        if 'hunt is empowered by' in line.lower():
                            # Extract gem numbers from this line
                            gem_matches = re.findall(r'\[(\d+)/', line)
                            for match in gem_matches:
                                gem_val = int(match)
                                # Check which type this gem belongs to
                                for gem_range in gem_types.values():
                                    if gem_val in gem_range:
                                        active_gems.append(gem_val)
                                        break
                    if active_gems:
                        return active_gems
    return []

def get_inactive_gem_types(active_gems):
    """Determine which gem types are NOT active"""
    inactive_types = []
    for gem_type, gem_range in gem_types.items():
        # Check if any gem of this type is active
        has_active = any(g in gem_range for g in active_gems)
        if not has_active:
            inactive_types.append(gem_type)
    return inactive_types

def select_gems_to_use(available_gems, inactive_types):
    """Select highest gems from inactive types only"""
    selected_gems = []
    
    for gem_type in inactive_types:
        gem_range = gem_types[gem_type]
        # Find gems of this type that you actually own
        type_gems = [g for g in available_gems if g in gem_range]
        if type_gems:
            # Get the highest one
            highest = max(type_gems)
            selected_gems.append(highest)
    
    return sorted(selected_gems)

def format_gem_command(gems):
    """Format gems into ouse command"""
    formatted_gems = ' '.join([f"{g:03d}" for g in gems])
    return f"ouse {formatted_gems}"

# Test notification on startup
# notify_captcha()  # Uncomment this line to test if notification works

while True:
    message = "oh"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36",
        "authorization": token,
        "referrer": channel_url
    }
    
    data = {
        "content": message
    }
        
    status = requests.post(url, json=data, headers=header)
    print(status)

    # Gửi tin nhắn thứ hai
    message = "ob"
    data = {
        "content": message
    }
    
    status = requests.post(url, json=data, headers=header)
    print(status)

    message = "owo"
    data = {
        "content": message
    }
    status = requests.post(url, json=data, headers=header)
    print(status)
    
    # Check for captcha after sending commands
    time.sleep(1)  # Wait a moment for bot response
    if check_for_captcha():
        notify_captcha()  # Send notification alert
        print("\n⚠️  CAPTCHA DETECTED! ⚠️")
        print("Pausing requests until captcha is resolved...")
        wait_for_captcha_resolution(max_wait_minutes=30)  # Wait up to 30 minutes
        # After captcha is resolved or timeout, continue the loop
    
    message_count += 2  # Tăng số lượng tin nhắn đã gửi
    riel_count += 1
    # Kiểm tra xem đã gửi đủ 30 tin nhắn chưa
    print(riel_count)
    if message_count >= 30:
        wait_time = random.randint(60, 300)  # Thời gian nghỉ ngẫu nhiên từ 1 -> 5 phút
        print(f"Nghỉ {wait_time} giây ({wait_time // 60} phút {wait_time % 60} giây)...")
        time.sleep(wait_time)  # Nghỉ ngẫu nhiên
        message_count = 0  # Đặt lại số lượng tin nhắn
    if riel_count >= 75:
        cnt += 1
        
        # Check which gems are currently active
        print("Checking active gems...")
        active_gems = check_active_gems()
        print(f"Active gems: {active_gems}")
        
        # Determine which gem types are NOT active
        inactive_types = get_inactive_gem_types(active_gems)
        print(f"Inactive gem types: {inactive_types}")
        
        # Only proceed if there are inactive types
        if not inactive_types:
            print("All gem types are already active, no need to use gems!")
            riel_count = 0
        else:
            # Get inventory and parse available gems
            print("Fetching inventory...")
            inventory = get_inventory()
            available_gems = parse_gems_from_inventory(inventory)
            print(f"Available gems in inventory: {available_gems}")
            
            if available_gems:
                # Select highest gems from inactive types only
                selected_gems = select_gems_to_use(available_gems, inactive_types)
                
                if selected_gems:
                    # Show which gems are the highest for each type
                    for gem_type in inactive_types:
                        type_range = gem_types[gem_type]
                        type_gems = [g for g in available_gems if g in type_range]
                        if type_gems:
                            print(f"{gem_type}: available {type_gems}, using {max(type_gems)}")
                    
                    message = format_gem_command(selected_gems)
                    print(f"Using gems: {message}")
                    
                    data = {
                        "content": message
                    }
                    
                    status = requests.post(url, json=data, headers=header)
                    print(status)
                else:
                    print("No gems available for inactive types!")
            else:
                print("Couldn't fetch inventory!")
            
            riel_count = 0
    if cnt >= 2: 
        wait_time = random.randint(60 * 30, 60 * 60)
        hours = wait_time // 3600
        minutes = (wait_time % 3600) // 60
        print(f"Nghỉ {hours} giờ {minutes} phút ({wait_time} giây)...")
        time.sleep(wait_time)
        cnt = 0
    # Thời gian chờ ngẫu nhiên từ 30 đến 60 giây
    wait_time = random.randint(15, 30) + 1
    time.sleep(wait_time)