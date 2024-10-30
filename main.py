import collections   
import pandas as pd   
import matplotlib.pyplot as plt   
from PIL import Image
from wordcloud import WordCloud
import nltk
nltk.download(["stopwords","vader_lexicon","punkt","wordnet"])
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from numpy import asarray
import json
from dotenv import load_dotenv
import os
import base64
import requests
import re
from requests import post
from lyricsgenius import Genius

#Load the environment variables
load_dotenv()

#Get the client ID and client secret from the environment variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")


def get_token_spotify():
    auth_string = SPOTIFY_CLIENT_ID + ":" + SPOTIFY_CLIENT_SECRET #concatenate the client ID and client secret into the string
    auth_bytes = auth_string.encode("utf-8") #encode the string into bytes
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8") #encode it using base64, this returns a base64 object and we need to convert that into a string so that we can pass it with the headers when we send the request

    url = "https://accounts.spotify.com/api/token" #this is the endpoint we are sending the request to
    headers = { #headers will be associated with our request
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data) #body of the request
    json_result = json.loads(result.content) #now we return json data in the .content field form the result object
    token = json_result["access_token"]
    return token

def get_auth_header_spotify(token):
    return {"Authorization": "Bearer " + token}

def get_auth_header_genius():
    return {"Authorization": "Bearer " + GENIUS_ACCESS_TOKEN}

token_spotify = get_token_spotify()
token_genius = GENIUS_ACCESS_TOKEN
genius = Genius(token_genius)

genius.verbose = False
genius.remove_section_headers = True
genius.skip_non_songs = False
genius.excluded_terms = ["(Remix)", "(Live)"]

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header_spotify(token) 
    params = {}  
    
    response = requests.get(url, headers=headers, params=params)  # Make the GET request
    if response.status_code != 200:  # Handle errors
        raise Exception(f"Failed to fetch playlist: {response.status_code}, {response.text}")
    
    return response.json()  # Return the JSON data

def display_playlist_tracks(playlist_data):
    tracks = playlist_data['tracks']['items']
    count_not_found = 0

    for idx, item in enumerate(tracks):
        track = item['track']
        track_name = track['name']  
        artist_name = ", ".join([artist['name'] for artist in track['artists']])  
        album_name = track['album']['name'] 

        title = remove_emojis(track_name)
        author = track['artists'][0]['name']
        print(title,author)
        
        song = genius.search_song(title,author)
        
        if song==None:
          count_not_found+=1
        print(f"{idx+1}. {track_name} by {artist_name} from the album {album_name}")
    print("Not found: ",count_not_found)

def search_song(song_title):
    headers = get_auth_header_genius()
    params = {"q": song_title}

    response = requests.get("https://api.genius.com/search", headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def extract_song_info(response_data):
    if response_data is None:
        return None

    hits = response_data.get("response", {}).get("hits", [])    
    hit = hits[0]
    song = hit.get("result", {})
    song_data = {
        "title": song.get("title"),
        "artist": song.get("primary_artist", {}).get("name"),
        "id":song.get("id")
    }

    return song_data

def remove_emojis(text):
    # Define the regex pattern to match all Unicode emoji characters
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )

    # Use the sub function to remove emojis
    return emoji_pattern.sub(r'', text)

def get_lyrics_lyricsovh(artist, title):
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("lyrics")
    else:
        return None


playlist_id_Sweden = "37i9dQZEVXbKVvfnL1Us06"
playlist_id_Italy = "37i9dQZEVXbJUPkgaWZcWG"
playlist_id_USA = "37i9dQZEVXbLp5XoPON0wI"
playlist_id_Mexico = "37i9dQZEVXbKUoIkUXteF6"
playlist_id_Argentina = "37i9dQZEVXbKPTKrnFPD0G"
playlist_id_Brazil = "37i9dQZEVXbKzoK95AbRy9"
playlist_ids = [
    playlist_id_Sweden, playlist_id_Italy, playlist_id_Brazil, playlist_id_Argentina,playlist_id_Mexico,playlist_id_USA
]

for playlist_id in playlist_ids:
  playlist_data = get_playlist_tracks(token_spotify, playlist_id)
  display_playlist_tracks(playlist_data)

"""
response = search_song("Home Drake")
song_info = extract_song_info(response)

if song_info:
        print(f"   Title: {song_info['title']}")
        print(f"   Artist: {song_info['artist']}")
        print(f"   ID: {song_info['id']}")
else:
    print("No results found.")
"""

