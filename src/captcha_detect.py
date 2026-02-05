"""
Captcha detection module - handles captcha detection and alerts
"""
import re
import time
import unicodedata
import requests
from initialization import HAS_WINSOUND, HAS_PLYER, BASE_URL, get_headers


_ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u2060\ufeff]")


def _normalize_text(value: str) -> str:
    """Normalize text to improve keyword matching across obfuscated messages."""
    if not value:
        return ""
    # Unicode normalize and strip combining marks
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    # Remove zero-width chars and collapse whitespace
    normalized = _ZERO_WIDTH_RE.sub("", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.lower().strip()


def check_for_captcha(token):
    """Check if bot is asking for captcha verification"""
    response = requests.get(BASE_URL + "?limit=1", headers=get_headers(token))
    print(f"DEBUG: Captcha check status={response.status_code}")
    if response.status_code != 200:
        print(f"DEBUG: Captcha check error body={response.text}")
    if response.status_code == 200:
        messages = response.json()
        print(f"DEBUG: Captcha check messages={len(messages)}")
        for msg in messages:
            raw_parts = [msg.get('content', '')]
            content = _normalize_text(msg.get('content', ''))
            # Check embeds too
            if 'embeds' in msg and msg['embeds']:
                for embed in msg['embeds']:
                    description = _normalize_text(embed.get('description', ''))
                    title = _normalize_text(embed.get('title', ''))
                    raw_parts.append(embed.get('description', ''))
                    raw_parts.append(embed.get('title', ''))
                    content += ' ' + description + ' ' + title
                    # Include embed fields and author text if present
                    for field in embed.get('fields', []):
                        content += ' ' + _normalize_text(field.get('name', ''))
                        content += ' ' + _normalize_text(field.get('value', ''))
                        raw_parts.append(field.get('name', ''))
                        raw_parts.append(field.get('value', ''))
                    author = embed.get('author', {})
                    content += ' ' + _normalize_text(author.get('name', ''))
                    raw_parts.append(author.get('name', ''))

                    raw_message = " ".join(part for part in raw_parts if part)
                    print(f"DEBUG: Message content: {raw_message}")
            
            # Check for captcha keywords
            captcha_keywords = [
                'captcha',
                'verify',
                'verification',
                'are you a real human',
                'verify that you are human',
                'please complete your captcha',
                'please complete this within 10 minutes',
                'please complete this within 120 minutes',
                'owobot.com/captcha'
            ]
            if any(keyword in content for keyword in captcha_keywords):
                print(f"DEBUG: Captcha message detected: {raw_message}")
                return True
    return False


def notify_captcha():
    """Send notification alert for captcha"""
    # Play alert sound - 3 beeps
    if HAS_WINSOUND:
        for i in range(3):
            import winsound
            winsound.Beep(1000, 500)  # 1000 Hz for 500ms
            time.sleep(0.3)
    
    # Try to show notification using plyer
    if HAS_PLYER:
        try:
            from plyer import notification
            notification.notify(
                title='⚠️ CAPTCHA DETECTED',
                message='OwO Bot requires captcha verification!\nPlease check Discord.',
                app_name='OwO Bot',
                timeout=10
            )
        except:
            pass
    
    # Always print to console as fallback
    print("\n" + "="*50)
    print("⚠️  CAPTCHA ALERT! ⚠️" * 3)
    print("="*50 + "\n")



def wait_for_captcha_resolution(token, max_wait_minutes=60*24):
    """Wait for captcha to be resolved, then resume
    
    Args:
        token: Discord token for API requests
        max_wait_minutes: Maximum time to wait before resuming anyway (default 30 min)
    """
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 360 
    check_interval = 30  # Check every 30 seconds
    
    print(f"\n⏳ PAUSED: Waiting for captcha to be resolved...")
    print(f"Will resume automatically in {max_wait_minutes} minutes if not resolved.")
    print(f"Complete the captcha in Discord to resume immediately.\n")
    
    while True:
        elapsed = time.time() - start_time
        
        # Check if captcha is still there
        if not check_for_captcha(token):
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
