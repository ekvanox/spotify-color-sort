# Spotify Color Sort

[![Version](https://img.shields.io/github/v/release/ekvanox/spotify-color-sort)](https://img.shields.io/github/v/release/ekvanox/spotify-color-sort)
![GitHub repo size](https://img.shields.io/github/repo-size/ekvanox/spotify-color-sort)
[![CodeFactor](https://www.codefactor.io/repository/github/ekvanox/spotify-color-sort/badge)](https://www.codefactor.io/repository/github/ekvanox/spotify-color-sort)
![License](https://img.shields.io/github/license/ekvanox/spotify-color-sort)

Spotify Color Sort is a script that sorts your Spotify playlists based on the dominant color of the album covers. It uses the Spotify API to interact with your playlists and downloads album covers, and then reorders the songs based on the color of their album covers.

![Example - Before/After](https://github.com/ekvanox/spotify-color-sort/blob/master/media/before-after.jpg)

## Requirements

- Python 3
- Spotify developer account

## Details

Spotify Color Sort operates by interfacing with the Spotify API and extracting key details about your playlists. The algorithm functions in the following steps:

1. **Accessing Playlist Details**: The script first retrieves your Spotify playlists and asks you to select one or more that you wish to sort.

2. **Retrieving Album Covers**: For each song in the selected playlists, the script downloads the album cover image. It maintains a cache of downloaded images to speed up future operations and minimize network requests.

3. **Color Extraction**: The script calculates the dominant color from each album cover. It uses the Python Imaging Library (PIL) to open each image and computes the average of the RGB values across all pixels.

4. **Sorting**: The script then sorts the colors using the HSV (Hue, Saturation, Value) color space. By converting the average RGB values to HSV, it can sort the songs based on their hue, which provides a more perceptually meaningful color ordering than sorting based on RGB values alone.

5. **Reordering Playlist**: Finally, the script reorders the songs in the playlist based on the sorted color values.

### Limitations

The algorithm has a few limitations:

- **Color Perception**: While the script sorts songs based on the average color of their album covers, this might not always correspond to the perceived "dominant" color of an album cover due to the complex ways in which humans perceive color.

- **Processing Time**: The processing time can be long for large playlists due to the time taken to download and process each image, and to reorder the playlist through the Spotify API.

- **Spotify API Rate Limits**: The Spotify API has rate limits which, when exceeded, can slow down the script or cause it to fail. These limits are usually not a problem for normal usage, but they could be an issue when processing large playlists or running the script multiple times in a short period.

## Installation

Clone the repository and install the required packages:

```sh
$ git clone https://github.com/ekvanox/spotify-color-sort
$ cd spotify-color-sort
$ pip install -r requirements.txt
```

## Usage

To run the script, use the following command:

```sh
$ python main.py
```

## Configuration

The script requires Spotify API credentials to function. These should be provided as environment variables SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.

If you're unsure of how to obtain these, please follow the guide provided by Spotify [here](https://developer.spotify.com/documentation/web-api/concepts/apps#register-your-app).

## License
This project is licensed under the MIT License - see the LICENSE file for details.