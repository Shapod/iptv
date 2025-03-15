import requests
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
import sys
import random
import traceback

# Force IPv4 connections
socket.getaddrinfo = lambda host, port, family=0, type=0, proto=0, flags=0: \
    [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (socket.gethostbyname(host), port)]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

def create_session():
    session = requests.Session()
    retry = Retry(
        total=7,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['GET']
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fetch_playlist():
    BASE_DOMAIN = "bdixtv.live"
    BASE_URL = f"http://{BASE_DOMAIN}/we/"
    
    try:
        session = create_session()
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",
            "Referer": BASE_URL
        }

        # Initial connection test
        print(f"Resolving {BASE_DOMAIN}...")
        try:
            ip = socket.gethostbyname(BASE_DOMAIN)
            print(f"Resolved IP: {ip}")
        except socket.gaierror:
            print("DNS resolution failed")
            sys.exit(1)

        print(f"Connecting to {BASE_URL}...")
        try:
            response = session.get(
                BASE_URL,
                headers=headers,
                timeout=30,
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()
        except requests.exceptions.SSLError:
            print("Falling back to SSL bypass...")
            response = session.get(
                BASE_URL,
                headers=headers,
                timeout=30,
                verify=False
            )

        print(f"HTTP {response.status_code} | Size: {len(response.text)} bytes")

        # Channel extraction
        soup = BeautifulSoup(response.text, 'html.parser')
        channels = []
        
        for a in soup.find_all('a', {'onclick': True}):
            if stream_match := re.search(r"stream=([^']+)", a['onclick']):
                stream_id = stream_match.group(1)
                img = a.find('img')
                channel_name = img['alt'].strip() if img else stream_id
                channels.append((channel_name, stream_id))

        if not channels:
            print("No channels found in page source")
            sys.exit(1)

        # Process channels
        playlist = ["#EXTM3U"]
        for channel_name, stream_id in channels:
            try:
                print(f"Processing: {channel_name}")
                play_url = f"{BASE_URL}play.php?stream={stream_id}"
                
                # Rotate headers
                headers.update({
                    "User-Agent": random.choice(USER_AGENTS),
                    "Referer": play_url
                })
                
                channel_res = session.get(
                    play_url,
                    headers=headers,
                    timeout=25,
                    verify=False
                )
                
                if m3u8_match := re.search(r'(https?://[^\s]+index\.m3u8\?token=[^\'"]+)', channel_res.text):
                    playlist.append(f"#EXTINF:-1,{channel_name}\n{m3u8_match.group(1)}")
                
            except Exception as e:
                print(f"Error processing {channel_name}: {str(e)}")

        # Save playlist
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(playlist))
        print(f"Successfully saved {len(playlist)-1} channels")

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    fetch_playlist()