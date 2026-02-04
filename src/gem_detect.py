"""
Gem detection and usage module - handles inventory, gem detection, and gem usage
"""
import os
import re
import time
import requests
from initialization import GEM_TYPES, BASE_URL, get_headers


def use_star_gems():
    """Return True if star gems (type5) should be used."""
    value = os.getenv("USE_STAR_GEMS", "true").strip().lower()
    return value in ("1", "true", "yes", "y", "on")


def get_inventory(token):
    """Fetch inventory by sending oinv command and reading the response"""
    message = "oinv"
    data = {"content": message}
    
    requests.post(BASE_URL, json=data, headers=get_headers(token))
    time.sleep(3)  # Wait longer for bot response
    
    # Get recent messages
    response = requests.get(BASE_URL + "?limit=15", headers=get_headers(token))
    if response.status_code == 200:
        messages = response.json()
        for msg in messages:
            # Check message content first
            content = msg.get('content', '')
            if 'Inventory' in content or 'inventory' in content.lower():
                return content
            
            # Check embeds
            if 'embeds' in msg and msg['embeds']:
                for embed in msg['embeds']:
                    title = embed.get('title', '').lower()
                    description = embed.get('description', '')
                    
                    # Check for inventory keywords
                    if ('inventory' in title or 'kurt' in title) and description:
                        return description
    
    return None


def parse_gems_from_inventory(inventory_text):
    """Parse gem IDs from inventory text"""
    if not inventory_text:
        return []
    
    # Find all 3-digit numbers that look like gem IDs (051-126)
    # The format is like: 051 ❤️ 27  or  051 (with emoji and count)
    gems = re.findall(r'\b(0?[0-9]{2,3})\b', inventory_text)
    
    # Filter to only include gem IDs in our ranges
    valid_gems = []
    for g in gems:
        gem_id = int(g)
        # Check if this gem ID is in any of our defined ranges
        for gem_range in GEM_TYPES.values():
            if gem_id in gem_range:
                valid_gems.append(gem_id)
                break
    
    # Remove duplicates and sort
    valid_gems = sorted(list(set(valid_gems)))
    return valid_gems


def check_active_gems(token):
    """Check which gem types are currently active by reading recent hunt messages"""
    response = requests.get(BASE_URL + "?limit=15", headers=get_headers(token))
    if response.status_code == 200:
        messages = response.json()
        for msg in messages:
            # Check message content
            content = msg.get('content', '').lower()
            if 'hunt is empowered by' in content:
                return parse_active_gems_from_text(msg.get('content', ''))
            
            # Check all embeds
            if 'embeds' in msg and msg['embeds']:
                for embed in msg['embeds']:
                    description = embed.get('description', '').lower()
                    title = embed.get('title', '').lower()
                    
                    if 'hunt is empowered by' in description or 'hunt is empowered by' in title:
                        full_text = embed.get('description', '') + ' ' + embed.get('title', '')
                        return parse_active_gems_from_text(full_text)
    
    return []


def parse_active_gems_from_text(text):
    """Parse active gem types from hunt empowerment text"""
    # Pattern to match raritygemN format (e.g., egem3, mgem1, rgem4)
    gem_matches = re.findall(r'([a-z])gem(\d+)', text)
    
    active_gem_types = []
    
    for rarity, gem_num in gem_matches:
        gem_type_num = int(gem_num)
        gem_type = f"type{gem_type_num}"
        
        # Check if this type exists in GEM_TYPES
        if gem_type in GEM_TYPES:
            if gem_type not in active_gem_types:  # Avoid duplicates
                active_gem_types.append(gem_type)
    
    # Special case: Check for star rarity gems (type5 - star rarity)
    if 'star' in text.lower() or '★' in text:
        if 'type5' not in active_gem_types:
            active_gem_types.append('type5')
    
    return active_gem_types


def get_inactive_gem_types(active_gem_types):
    """Determine which gem types are NOT active"""
    inactive_types = []
    for gem_type in GEM_TYPES.keys():
        if gem_type == "type5" and not use_star_gems():
            continue
        # Check if this type is in active gems
        if gem_type not in active_gem_types:
            inactive_types.append(gem_type)
    return inactive_types


def select_gems_to_use(available_gems, inactive_types):
    """Select highest gems from inactive types only"""
    selected_gems = []
    
    for gem_type in inactive_types:
        if gem_type == "type5" and not use_star_gems():
            continue
        gem_range = GEM_TYPES[gem_type]
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


def get_highest_gems_by_type(available_gems):
    """Get the highest gem ID for each type"""
    selected_gems = []
    
    for gem_type, gem_range in GEM_TYPES.items():
        # Find gems of this type
        type_gems = [g for g in available_gems if g in gem_range]
        if type_gems:
            # Get the highest one
            highest = max(type_gems)
            selected_gems.append(highest)
    
    return sorted(selected_gems)[:3]  # Return top 3 gems
