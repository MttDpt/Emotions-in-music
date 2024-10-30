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
import numpy as np

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

song_lyrics=[]
stop_words_en=stopwords.words('english')
stop_words_en.extend(['or', 'm', 'ma', 'ours', 'against', 'nor', "it's", 'o', 
'wasn', 'hasn', 'my', 'had', 'didn', 'isn', 'did', 'aren', 'those', 'than', 
"mustn't", "you've", 'to', 'she', 'having', "haven't", 'into', 't', 'll', 
'himself', 'do', "that'll", 'so', 'of', 'on', 'very', 'for', 'out', 'were', 
'should', 'they', 'ain', "should've", 'you', "didn't", 'yours', 'was', 'our',
 'can', 'myself', "shouldn't", 'have', 'up', 'mightn', "you'll", 'any', 
'itself', 'hadn', 'him', 'doesn', 'weren', 'y', 'being', "don't", 'them', 
'are','and', 'that', 'your', 'yourself', 'their', 'some', 'ourselves', 've', 
'doing', 'been', 'shouldn', 'yourselves', "mightn't", 'most', 'because',
 'few', 'wouldn', "you'd", 'through', "you're", 'themselves', 'an', 'if',
 "wouldn't", 'its', 'other', "won't", "wasn't", "she's", 'we', 'shan',
 "weren't",'don',"hadn't", 'this', 'off', 'while', 'a', 'haven', 'her', 
'theirs', 'all', "hasn't", "doesn't", 'about', 'then', 'by','such', 'but', 
'until', 'each', 'there', "aren't", 'with', 'not', "shan't", 'hers', 'it', 
'too', 'i', 'at', 'is', 'as', 'me', 'herself', 's', 'the', 'where', 'am', 
'has', 'over', "couldn't", 'when', 'does', 'mustn','re', 'no', 'in', 'who', 
'd', 'own', 'he', 'be', "isn't", 'his', 'these', 'same', 'whom', 'will', 
'needn','couldn', 'from'])
stop_words_es=stopwords.words('spanish')
stop_words_su=stopwords.words('swedish')
stop_words_it=stopwords.words('italian')

stop_words = [*stop_words_en,*stop_words_es,*stop_words_it,*stop_words_su]

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
        else:
          song_lyrics.append(song.lyrics)  
          print(f"{idx+1}. {track_name} by {artist_name} from the album {album_name}")

    print("Number of not found: ",count_not_found)

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

def preprocess_text(text):
    tokeniser = RegexpTokenizer(r'[A-Za-z]+')
    tokens = tokeniser.tokenize(text)
    
    data_token=[token.lower() for token in tokens]
    processed_words= [w for w in data_token if not w in stop_words]

    return processed_words[3:(len(processed_words)-1)]

playlist_id_Sweden = "37i9dQZEVXbKVvfnL1Us06"
playlist_id_Italy = "37i9dQZEVXbJUPkgaWZcWG"
playlist_id_USA = "37i9dQZEVXbLp5XoPON0wI"
playlist_id_Mexico = "37i9dQZEVXbKUoIkUXteF6"
playlist_id_Argentina = "37i9dQZEVXbKPTKrnFPD0G"
playlist_id_Brazil = "37i9dQZEVXbKzoK95AbRy9"
playlist_ids = [
    playlist_id_Sweden
    #, playlist_id_Italy, playlist_id_Brazil, playlist_id_Argentina,playlist_id_Mexico,playlist_id_USA
]

for playlist_id in playlist_ids:
  playlist_data = get_playlist_tracks(token_spotify, playlist_id)
  display_playlist_tracks(playlist_data)

cleaned_words = np.array([])
for song in song_lyrics:
    processed_song = preprocess_text(song)
    np_processed_song = np.array(processed_song)
    cleaned_words = np.concatenate((cleaned_words,np_processed_song))

print(len(cleaned_words))

unique_cleaned_words = np.unique(cleaned_words)
print(len(unique_cleaned_words))


