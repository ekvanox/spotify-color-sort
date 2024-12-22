import logging
from pathlib import Path
import requests
from tqdm import tqdm
import questionary
from spotify import sp, get_user_data_and_playlists
from image_processing import get_average_color, get_sort_key
import coloredlogs
from time import time

logger = logging.getLogger()
logger.disabled = True
logger = logging.getLogger(__name__)

# Setup logging
coloredlogs.install(
    level=20,
    fmt="[%(levelname)s] %(asctime)s: %(message)s",
    level_styles={
        "critical": {"bold": True, "color": "red"},
        "debug": {"color": "green"},
        "error": {"color": "red"},
        "info": {"color": "white"},
        "notice": {"color": "magenta"},
        "spam": {"color": "green", "faint": True},
        "success": {"bold": True, "color": "green"},
        "verbose": {"color": "blue"},
        "warning": {"color": "yellow"},
    },
    logger=logger,
    field_styles={
        "asctime": {"color": "cyan"},
        "levelname": {"bold": True, "color": "black"},
    },
)

try:
    # Get user data and playlists
    user, user_playlists = get_user_data_and_playlists()
except ValueError as e:
    logger.error(str(e))
    exit(1)

# Create a list of choices for the user to select from.
# Each choice is a string that contains the index and name of a playlist.
choices = [f"{i}: {p['name']}" for i, p in enumerate(user_playlists, 1)]

# Ask the user to select from the list of choices.
# The selected choices will be stored in the 'answers' variable.
answers = questionary.checkbox(
    'Please select the playlists to sort:',
    choices=choices
).ask()
selected_playlists = [user_playlists[int(answer.split(':')[0])-1] for answer in answers]

# Start timer to calculate the playlist sorting time
start_time = time()

# Get all song album cover urls from selected playlists and process each playlist
for selected_playlist in selected_playlists:
    logger.info(f'Processing playlist: {selected_playlist["name"]}')

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

        # Get color data
        color_data = get_average_color(image_path)
        colors.append([song_id, color_data])

    # Sort using the new color approach
    colors.sort(key=lambda item: get_sort_key(item[1]))

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

if (num_playlists := len(selected_playlists)):
    logger.info(f'{num_playlists} playlist(s) sorted in {time() - start_time:.1f}s')
else:
    logger.error('No playlists selected, exiting...')