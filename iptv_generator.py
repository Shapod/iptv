import requests
from bs4 import BeautifulSoup
import re
import traceback
import sys

def fetch_playlist():
    BASE_URL = "http://172.20.2.5/we/"
    PLAY_URL_TEMPLATE = "http://172.20.2.5/we/play.php?stream={}"
    M3U8_PATTERN = re.compile(r'http:\/\/172\.20\.2\.5:8082\/.*?\/index\.m3u8\?token=[^\'"]+')
    
    try:
        print("Fetching main page...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": BASE_URL
        }
        
        # Get main page content
        main_page = requests.get(BASE_URL, headers=headers, timeout=10)
        main_page.raise_for_status()
        print("Main page fetched successfully")

        # Parse channels
        soup = BeautifulSoup(main_page.text, 'html.parser')
        channels = []
        seen_streams = set()

        print("Extracting channel links...")
        for a in soup.find_all('a', {'onclick': True}):
            onclick = a.get('onclick', '')
            stream_match = re.search(r"stream=([^']+)", onclick)
            if stream_match:
                stream_id = stream_match.group(1)
                if stream_id not in seen_streams:
                    seen_streams.add(stream_id)
                    img = a.find('img')
                    channel_name = img.get('alt', stream_id).strip() if img else stream_id
                    channels.append((channel_name, stream_id))
                    print(f"Found channel: {channel_name}")

        if not channels:
            print("No channels found!")
            sys.exit(1)

        # Generate playlist
        playlist = ["#EXTM3U"]
        success_count = 0
        
        print("\nProcessing channels:")
        for idx, (channel_name, stream_id) in enumerate(channels, 1):
            try:
                print(f"{idx}/{len(channels)}: {channel_name}")
                play_url = PLAY_URL_TEMPLATE.format(stream_id)
                response = requests.get(play_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Find m3u8 URL
                match = M3U8_PATTERN.search(response.text)
                if match:
                    m3u8_url = match.group(0)
                    playlist.append(f"#EXTINF:-1, {channel_name}\n{m3u8_url}")
                    success_count += 1
                else:
                    print(f"  No M3U8 found for {channel_name}")

            except Exception as e:
                print(f"  Error processing {channel_name}: {str(e)}")

        print(f"\nSuccessfully processed {success_count}/{len(channels)} channels")
        
        if success_count == 0:
            print("Critical error: No streams found!")
            sys.exit(1)

        # Write playlist file
        try:
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write('\n'.join(playlist))
            print("Playlist file created successfully")
            
        except IOError as e:
            print(f"File write error: {str(e)}")
            sys.exit(1)

    except requests.RequestException as e:
        print(f"Network error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    fetch_playlist()