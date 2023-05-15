import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify and environment setup
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri='http://localhost:8080'
scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'

if not all([client_id, client_secret]):
    raise ValueError("Please set the SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in the environment")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

def get_user_data_and_playlists():
    user = sp.current_user()
    response = sp.current_user_playlists(limit=50)
    user_playlists = [p for p in response['items'] if p['owner']['id'] == user['id']]
    return user, user_playlists
