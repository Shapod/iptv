import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
import traceback
import sys
import random

# Configuration
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_playlist():
    BASE_URL = "http://bdixtv.live/we/"
    PLAY_URL_TEMPLATE = f"{BASE_URL}play.php?stream={{}}"
    M3U8_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+index\.m3u8\?token=[^\'"]+')
    
    try:
        session = create_session()
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": BASE_URL
        }

        print(f"Connecting to {BASE_URL}...")
        try:
            response = session.get(BASE_URL, headers=headers, timeout=25, verify=False)
            response.raise_for_status()
        except requests.exceptions.SSLError:
            print("SSL verification failed, retrying without verification...")
            response = session.get(BASE_URL, headers=headers, timeout=25, verify=False)
        
        print(f"Status: {response.status_code}")
        
        # Parse channels
        soup = BeautifulSoup(response.text, 'html.parser')
        channels = []
        seen_streams = set()

        print("Extracting channel links...")
        for a in soup.find_all('a', {'onclick': True}):
            onclick = a.get('onclick', '')
            if stream_match := re.search(r"stream=([^']+)", onclick):
                stream_id = stream_match.group(1)
                if stream_id not in seen_streams:
                    seen_streams.add(stream_id)
                    img = a.find('img')
                    channel_name = img.get('alt', stream_id).strip() if img else stream_id
                    channels.append((channel_name, stream_id))

        if not channels:
            print("Error: No channels found in page source")
            sys.exit(1)

        # Generate playlist
        playlist = ["#EXTM3U"]
        success_count = 0
        
        print(f"\nProcessing {len(channels)} channels:")
        for idx, (channel_name, stream_id) in enumerate(channels, 1):
            try:
                print(f"{idx:03d}/{len(channels)}: {channel_name}")
                play_url = PLAY_URL_TEMPLATE.format(stream_id)
                
                # Randomize headers for each request
                headers["User-Agent"] = random.choice(USER_AGENTS)
                channel_res = session.get(play_url, headers=headers, timeout=20, verify=False)
                channel_res.raise_for_status()
                
                if match := M3U8_PATTERN.search(channel_res.text):
                    m3u8_url = match.group(0)
                    playlist.append(f"#EXTINF:-1 tvg-name=\"{channel_name}\",{channel_name}\n{m3u8_url}")
                    success_count += 1
                else:
                    print(f"  No M3U8 found in response")

            except Exception as e:
                print(f"  Error: {str(e)}")

        print(f"\nSuccess rate: {success_count}/{len(channels)} channels")
        
        if success_count == 0:
            print("Critical error: No valid streams found")
            sys.exit(1)

        # Write playlist file
        try:
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write('\n'.join(playlist))
            print(f"\nPlaylist created with {success_count} channels")
            
        except IOError as e:
            print(f"File write error: {str(e)}")
            sys.exit(1)

    except requests.RequestException as e:
        print(f"Network error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    fetch_playlist()