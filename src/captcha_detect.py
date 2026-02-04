"""
Captcha detection module - handles captcha detection and alerts
"""
import requests
import time
from initialization import HAS_WINSOUND, HAS_PLYER, BASE_URL, get_headers


def check_for_captcha(token):
    """Check if bot is asking for captcha verification"""
    response = requests.get(BASE_URL + "?limit=15", headers=get_headers(token))
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
                    # Include embed fields and author text if present
                    for field in embed.get('fields', []):
                        content += ' ' + field.get('name', '').lower()
                        content += ' ' + field.get('value', '').lower()
                    author = embed.get('author', {})
                    content += ' ' + author.get('name', '').lower()
            
            # Check for captcha keywords
            captcha_keywords = [
                'captcha',
                'verify',
                'verification',
                'are you a real human',
                'verify that you are human',
                'please complete your captcha',
                'owobot.com/captcha'
            ]
            if any(keyword in content for keyword in captcha_keywords):
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
