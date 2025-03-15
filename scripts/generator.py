import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "http://172.16.172.114"
CHANNELS = {
    "ZeeBanglaHD": "Zee Bangla HD",
    "TSportsHD": "T Sports HD",
    "channel24": "channel24",
    # Add more channels
}

def generate_playlist():
    """Generate the M3U playlist content"""
    playlist = ["#EXTM3U"]
    
    for channel_id, channel_name in CHANNELS.items():
        try:
            r = requests.get(
                f"{BASE_URL}/player.php?stream={channel_id}",
                timeout=10
            )
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, 'html.parser')
            if source_tag := soup.find('source'):
                playlist.append(f"#EXTINF:-1,{channel_name}\n{source_tag['src']}")
            else:
                print(f"No source tag found for {channel_id}")
                
        except Exception as e:
            print(f"Error processing {channel_id}: {str(e)}")
    
    return '\n'.join(playlist)

if __name__ == "__main__":
    # Create directory if needed
    os.makedirs('channels', exist_ok=True)
    
    # Generate and save playlist
    playlist_content = generate_playlist()
    
    with open('channels/playlist.m3u', 'w') as f:
        f.write(playlist_content)
    
    print("Playlist generated successfully!")