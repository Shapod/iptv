import requests
from bs4 import BeautifulSoup
import re

def fetch_playlist():
    BASE_URL = "http://172.20.2.5/we/"
    PLAY_URL_TEMPLATE = "http://172.20.2.5/we/play.php?stream={}"
    M3U8_PATTERN = re.compile(r'http:\/\/172\.20\.2\.5:8082\/.*?\/index\.m3u8\?token=[^\'"]+')
    
    # Fetch main page to get channel list
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": BASE_URL
    }
    
    try:
        # Get all channels from main page
        main_page = requests.get(BASE_URL, headers=headers)
        main_page.raise_for_status()
        soup = BeautifulSoup(main_page.text, 'html.parser')
        
        channels = []
        seen_streams = set()
        
        # Extract channel names and stream IDs
        for a in soup.find_all('a', {'onclick': True}):
            onclick = a['onclick']
            stream_match = re.search(r"stream=([^']+)", onclick)
            if stream_match:
                stream_id = stream_match.group(1)
                if stream_id not in seen_streams:
                    seen_streams.add(stream_id)
                    img = a.find('img')
                    channel_name = img['alt'].strip() if img else stream_id
                    channels.append((channel_name, stream_id))

        # Fetch m3u8 URLs for each channel
        playlist = ["#EXTM3U"]
        for channel_name, stream_id in channels:
            try:
                # Get play.php page for the stream
                play_url = PLAY_URL_TEMPLATE.format(stream_id)
                response = requests.get(play_url, headers=headers)
                response.raise_for_status()
                
                # Find m3u8 URL in response
                match = M3U8_PATTERN.search(response.text)
                if match:
                    m3u8_url = match.group(0)
                    playlist.append(f"#EXTINF:-1, {channel_name}\n{m3u8_url}")
                    print(f"Found: {channel_name}")
                else:
                    print(f"Not found: {channel_name}")
            
            except Exception as e:
                print(f"Error fetching {channel_name}: {str(e)}")

        # Save playlist
        with open("playlist.m3u", "w") as f:
            f.write('\n'.join(playlist))
        
        print("Playlist generated successfully!")
        
    except Exception as e:
        print(f"Main error: {str(e)}")

if __name__ == "__main__":
    fetch_playlist()