import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify and environment setup
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri='http://localhost:8080'
scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'

if not all([client_id, client_secret]):
    raise ValueError(
        "Missing Spotify API credentials. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.\n"
        "You can obtain these credentials by:\n"
        "1. Visit https://developer.spotify.com/dashboard\n"
        "2. Create a new app\n"
        "3. Copy the Client ID and Client Secret\n"
        "4. Set them as environment variables:\n"
        "   export SPOTIFY_CLIENT_ID='your-client-id'\n"
        "   export SPOTIFY_CLIENT_SECRET='your-client-secret'"
    )

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

def get_user_data_and_playlists():
    user = sp.current_user()
    response = sp.current_user_playlists(limit=50)
    user_playlists = [p for p in response['items'] if p['owner']['id'] == user['id']]
    return user, user_playlists
