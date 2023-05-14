import os
import requests
import colorsys
from tqdm import tqdm
from pathlib import Path
from PIL import Image, ImageStat
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import questionary

def get_average_color(image_path):
    """Get the average color of the image."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        stat = ImageStat.Stat(img)
        r,g,b = stat.mean
        return r,g,b
    except Exception as e:
        print(f"Warning: Failed to open or process the image {image_path}. Error: {e}")
        return 0, 0, 0  # Return black if there is an error processing the image


# Spotify and environment setup
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri='http://localhost:8080'
scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'

if not all([client_id, client_secret]):
    raise ValueError("Please set the SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in the environment")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Get user data and playlists
user = sp.current_user()
response = sp.current_user_playlists(limit=50)
user_playlists = [p for p in response['items'] if p['owner']['id'] == user['id']]

# User playlist selection
answers = questionary.checkbox('Please select the playlists to sort:', choices=[f"{i}: {p['name']}" for i, p in enumerate(user_playlists, 1)]).ask()
selected_playlists = [user_playlists[int(answer.split(':')[0])-1] for answer in answers]

# Get all song album cover urls from selected playlists and process each playlist
for selected_playlist in selected_playlists:
    playlist_name = selected_playlist.split(':')[1]
    print('Processing: ', playlist_name)

    songs = []
    image_urls = []
    for offset in range(0, selected_playlist['tracks']['total'], 100):
        response = sp.playlist_items(playlist_id=selected_playlist['id'], offset=offset, limit=100)
        songs.extend(response['items'])
        image_urls.extend([(song['track']['album']['images'][-1]['url'], song['track']['id']) for song in response['items']])

    # Image processing and color extraction
    icon_path = Path('.') / 'cache'
    icon_path.mkdir(parents=True, exist_ok=True)
    colors = []
    for image_url, song_id in tqdm(image_urls, desc='Downloading images', leave=False):
        uid = image_url.split('/')[-1]
        image_path = icon_path / uid

        # Skip download if already cached
        if not image_path.exists():
            response = requests.get(image_url)
            response.raise_for_status()
            with open(image_path, 'wb') as f:
                f.write(response.content)

        # Get average color
        primary_color = get_average_color(image_path)
        colors.append([song_id, primary_color])

    # Apply HSV sorting to colors and reorder songs
    colors.sort(key=lambda item: colorsys.rgb_to_hsv(*item[1]))
    song_ids = [song['track']['id'] for song in songs]
    new_order = [song_id for song_id, _ in colors[::-1]]
    song_ids_order = {song_id: i for i, song_id in enumerate(new_order)}

    # Reorder the playlist
    insert_position = 0
    for song_id, _ in tqdm(colors, desc='Reordering songs', leave=False):
        current_position = song_ids.index(song_id)
        if current_position != insert_position:
            sp.playlist_reorder_items(selected_playlist['id'], range_start=current_position, insert_before=insert_position)
            song_ids.insert(insert_position, song_ids.pop(current_position))
        insert_position += 1
