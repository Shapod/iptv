import requests
from bs4 import BeautifulSoup
import os
import sys
from urllib.parse import urljoin

BASE_URL = "http://172.20.2.5/we"
CHANNELS = {
    "ZEE-BANGLA": "ZEE-BANGLA",
    "T-SPORTS": "T-SPORTS",
    "STAR-JALSHA": "STAR-JALSHA",
    # Add more channels
}

def fetch_channel_url(channel_id):
    """Fetch channel URL with detailed debugging"""
    try:
        url = f"{BASE_URL}/play.php?stream={channel_id}"
        print(f"\n🔍 Fetching: {url}")
        
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": BASE_URL
            },
            timeout=15
        )
        print(f"✅ Response: {response.status_code} ({len(response.text)} bytes)")

        # Debug: Save HTML response
        with open(f"debug_{channel_id}.html", "w") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')
        source_tag = soup.find('source')
        
        if not source_tag:
            print(f"❌ No <source> tag found in {channel_id} response")
            return None
            
        m3u8_url = source_tag.get('src')
        if not m3u8_url:
            print(f"❌ Empty src in <source> tag for {channel_id}")
            return None
            
        final_url = urljoin(BASE_URL, m3u8_url)
        print(f"🌐 Found URL: {final_url}")
        return final_url
        
    except Exception as e:
        print(f"🔥 Error in {channel_id}: {str(e)}", file=sys.stderr)
        return None

def generate_playlist():
    """Generate playlist with validation"""
    playlist = ["#EXTM3U x-tvg-url=\"\""]
    
    for channel_id, channel_name in CHANNELS.items():
        if url := fetch_channel_url(channel_id):
            playlist.append(
                f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{channel_name}",{channel_name}\n'
                f'{url}'
            )
    
    if len(playlist) == 1:
        raise ValueError("No channels found - check network access to server")
    
    return '\n'.join(playlist)

if __name__ == "__main__":
    try:
        os.makedirs('channels', exist_ok=True)
        playlist_content = generate_playlist()
        
        with open('channels/playlist.m3u', 'w', encoding='utf-8') as f:
            f.write(playlist_content)
            
        print(f"\n🎉 Success! Generated {len(playlist)-1} channels")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n💥 Critical failure: {str(e)}", file=sys.stderr)
        sys.exit(1)