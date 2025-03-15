from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)
executor = ThreadPoolExecutor(10)  # For concurrent channel fetching

# Configuration
BASE_URL = "http://172.16.172.114"
PORT = "8083"
CHANNELS = [
    {"name": "Zee Bangla HD", "id": "ZeeBanglaHD"},
    # Add more channels here
]

def fetch_channel_data(channel):
    """Fetch m3u8 URL for a single channel with retries"""
    retries = 3
    for attempt in range(retries):
        try:
            player_url = f"{BASE_URL}/player.php?stream={channel['id']}"
            response = requests.get(player_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": BASE_URL
            }, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if source_tag := soup.find('source'):
                return f"#EXTINF:-1 tvg-id=\"{channel['id']}\",{channel['name']}\n{source_tag['src']}\n"
            
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {channel['id']}: {str(e)}")
            time.sleep(2)
    
    return f"#EXTINF:-1,{channel['name']} [Unavailable]\n#EXTVLCOPT:no-http-reconnect\nhttp://0.0.0.0/unavailable\n"

@app.route('/playlist.m3u')
def generate_playlist():
    """Generate dynamic playlist with parallel fetching"""
    start_time = time.time()
    
    # Process channels concurrently
    futures = [executor.submit(fetch_channel_data, channel) for channel in CHANNELS]
    results = [future.result() for future in futures]
    
    # Build final playlist
    playlist = "#EXTM3U x-tvg-url=\"\"\n" + "".join(results)
    print(f"Generated playlist in {time.time()-start_time:.2f}s")
    
    return Response(playlist, mimetype='audio/mpegurl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)
