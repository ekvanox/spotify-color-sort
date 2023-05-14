import colorsys
from colorthief import ColorThief
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import questionary
import requests
from tqdm import tqdm
from pathlib import Path
from PIL import Image

client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

if not client_id:
    print('Please set the SPOTIFY_CLIENT_ID in the environment')
    exit(1)

if not client_secret:
    print('Please set the SPOTIFY_CLIENT_SECRET in the environment')
    exit(1)

redirect_uri='http://localhost:8080'
scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'

def get_average_color(image_path):
    try:
        img = Image.open(image_path)
        width, height = img.size
        channels = len(img.getpixel((0,0))) if img.mode != 'L' else 1

        if width == 0 or height == 0:
            print(f"Warning: Image {image_path} is empty.")
            return (0, 0, 0)  # Return black for empty image

        r_total = 0
        g_total = 0
        b_total = 0
        count = 0

        if channels == 3:  # RGB image
            for x in range(0, width):
                for y in range(0, height):
                    r, g, b = img.getpixel((x,y))
                    r_total += r
                    g_total += g
                    b_total += b
                    count += 1
        elif channels == 1:  # Grayscale image
            for x in range(0, width):
                for y in range(0, height):
                    gray = img.getpixel((x,y))
                    r_total += gray
                    g_total += gray
                    b_total += gray
                    count += 1

        return (r_total/count, g_total/count, b_total/count)
    except Exception as e:
        print(f"Warning: Failed to open or process the image {image_path}. Error: {e}")
        return (0, 0, 0)  # Return black if there is an error processing the image



# Login to spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# Download user data from spotify
user = sp.current_user()
response = sp.current_user_playlists(limit=50)
user_playlists = tuple(filter(lambda playlist: playlist['owner']['id'] == user['id'], response['items']))

# Make user select a playlist
answer = questionary.select(message='Please select a playlist to sort:',choices=[f"{i}: {p['name']}" for i, p in enumerate(user_playlists, 1)]).ask()
selected_playlist = user_playlists[int(answer.split(':')[0])-1]

# Get all song album cover urls from selected playlist
songs_downloaded = 0
songs = []
image_urls = []
while True:
    response = sp.playlist_items(playlist_id=selected_playlist['id'], offset=songs_downloaded, limit=100)
    new_songs = response['items']
    songs_downloaded += len(new_songs)
    songs.extend(new_songs)
    image_urls.extend([(song['track']['album']['images'][-1]['url'], song['track']['id']) for song in new_songs])

    if songs_downloaded == response['total']:
        break

# Define and create the icon cache directory
icon_path = Path('.') / Path('cache')
if not icon_path.exists():
    icon_path.mkdir(parents=True)

# Download images
colors = []
for image_url, song_id in tqdm(image_urls, desc='Downloading images'):
    uid = image_url.split('/')[-1]
    image_path = icon_path / Path(uid)

    # Skip download if already cached
    if not image_path.exists():
        with open(icon_path / Path(uid), 'wb+') as f:
            img = requests.get(image_url).content
            f.write(img)

    # Get average color
    primary_color = get_average_color(image_path)
    colors.append([song_id, primary_color])

# Apply HSV sorting to colors
colors.sort(key=lambda rgb: colorsys.rgb_to_hsv(*rgb[1]))

# Change the order of the playlist
song_ids = [song['track']['id'] for song in songs]
for song_id, _ in tqdm(colors[::-1], desc='Reordering songs'):
    index = song_ids.index(song_id)
    song_ids.insert(0, song_ids.pop(index))
    sp.playlist_reorder_items(selected_playlist['id'], range_start=index, insert_before=0)