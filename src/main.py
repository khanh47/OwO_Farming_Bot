"""
Main bot loop - orchestrates OwO bot farming with gem management and captcha handling
"""
import requests
import time
import random

from initialization import (
    load_token, get_headers, BASE_URL, GEM_TYPES,
    ITERATION_WAIT_MIN, ITERATION_WAIT_MAX,
    SHORT_BREAK_MIN, SHORT_BREAK_MAX,
    LONG_BREAK_MIN, LONG_BREAK_MAX
)
from captcha_detect import check_for_captcha, notify_captcha, wait_for_captcha_resolution
from gem_detect import (
    get_inventory,
    parse_gems_from_inventory,
    check_active_gems,
    get_inactive_gem_types,
    select_gems_to_use,
    format_gem_command
)


def send_command(token, message):
    """Send a command message to Discord"""
    data = {"content": message}
    return requests.post(BASE_URL, json=data, headers=get_headers(token))


def main():
    """Main bot loop"""
    # Load token at startup
    token = load_token()
    
    # Initialize counters
    message_count = 0
    riel_count = 0
    cnt = 0
    
    print("Bot started. Running indefinitely...\n")
    
    while True:
        # Send basic farming commands
        print("Sending farming commands...")
        send_command(token, "oh")
        send_command(token, "ob")
        send_command(token, "owo")
        
        # Check for captcha after sending commands
        time.sleep(1)  # Wait a moment for bot response
        if check_for_captcha(token):
            notify_captcha()  # Send notification alert
            print("\n⚠️  CAPTCHA DETECTED! ⚠️")
            print("Pausing requests until captcha is resolved...")
            wait_for_captcha_resolution(token, max_wait_minutes=360)  # Wait up to 6 hours
       
        if riel_count % 10 == 0 and riel_count > 0:
            # Check which gems are currently active
            print("Checking active gems...")
            active_gem_types = check_active_gems(token)
            print(f"Active gem types: {active_gem_types}")
        
            # Determine which gem types are NOT active
            inactive_types = get_inactive_gem_types(active_gem_types)
            print(f"Inactive gem types: {inactive_types}")
        
            # Only proceed if there are inactive types
            if not inactive_types:
                print("All gem types are already active, no need to use gems!")
                riel_count = 0
            else:
                # Get inventory and parse available gems
                print("Fetching inventory...")
                inventory = get_inventory(token)
                available_gems = parse_gems_from_inventory(inventory)
                print(f"Available gems in inventory: {available_gems}")
                
                if available_gems:
                    # Select highest gems from inactive types only
                    selected_gems = select_gems_to_use(available_gems, inactive_types)
                    
                    if selected_gems:
                        # Show which gems are the highest for each type
                        for gem_type in inactive_types:
                            type_range = GEM_TYPES[gem_type]
                            type_gems = [g for g in available_gems if g in type_range]
                            if type_gems:
                                print(f"{gem_type}: available {type_gems}, using {max(type_gems)}")
                        
                        message = format_gem_command(selected_gems)
                        print(f"Using gems: {message}")
                        
                        send_command(token, message)
                    else:
                        print("No gems available for inactive types!")
                else:
                    print("Couldn't fetch inventory!")
        
        message_count += 2  # Increment message count
        riel_count += 1
        
        # Check if we've sent 30 messages - then rest
        print(f"Messages sent: {riel_count}")
        if message_count >= 30:
            wait_time = random.randint(SHORT_BREAK_MIN, SHORT_BREAK_MAX)
            print(f"Short break: {wait_time} seconds ({wait_time // 60} min {wait_time % 60} sec)...")
            time.sleep(wait_time)
            message_count = 0  # Reset message counter
        
        # Check riel count - after 75 riel, increment cycle counter
        if riel_count >= 75:
            cnt += 1
            riel_count = 0
        
        # After 2 full cycles, take a longer break
        if cnt >= 2:
            wait_time = random.randint(LONG_BREAK_MIN, LONG_BREAK_MAX)
            hours = wait_time // 3600
            minutes = (wait_time % 3600) // 60
            print(f"Long break: {hours}h {minutes}m ({wait_time} seconds)...")
            time.sleep(wait_time)
            cnt = 0
        
        # Random wait between iterations
        wait_time = random.randint(ITERATION_WAIT_MIN, ITERATION_WAIT_MAX)
        print(f"Waiting {wait_time} seconds before next iteration...\n")
        time.sleep(wait_time)


if __name__ == "__main__":
    main()