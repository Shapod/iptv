import os

# Create channels directory if not exists
os.makedirs('channels', exist_ok=True)

# Then write the file
with open('channels/playlist.m3u', 'w') as f:
    f.write('\n'.join(playlist))

import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "http://172.16.172.114"
CHANNELS = {
    "ZeeBanglaHD": "Zee Bangla HD",
    # Add more channels
}

def generate_playlist():
    playlist = ["#EXTM3U"]
    
    for channel_id, channel_name in CHANNELS.items():
        try:
            r = requests.get(f"{BASE_URL}/player.php?stream={channel_id}", timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            m3u8_url = soup.find('source')['src']
            playlist.append(f"#EXTINF:-1,{channel_name}\n{m3u8_url}")
            
        except Exception as e:
            print(f"Failed {channel_id}: {str(e)}")
    
    output_path = os.path.join('channels', 'playlist.m3u')
    with open(output_path, 'w') as f:
        f.write('\n'.join(playlist))

if __name__ == "__main__":
    generate_playlist()
