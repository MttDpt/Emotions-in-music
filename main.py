# Loading all necessary libraries
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

#API CALL
#Import dotenv package
from dotenv import load_dotenv
import os
import base64
import requests
from requests import post

#Load the environment variables
load_dotenv() #make sure to name the .env file correctly and to have it in the same directory of the main.py file  

#Get the client ID and client secret from the environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET #concatenate the client ID and client secret into the string
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

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

token = get_token()
print(token)

# Function to get playlist data
def get_playlist_tracks(token, playlist_id, market="ES"):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header(token)  # This will pass the token as the Authorization header
    params = {"market": market}  # Define market as "ES" for Spain (ISO country code)
    
    response = requests.get(url, headers=headers, params=params)  # Make the GET request
    if response.status_code != 200:  # Handle errors
        raise Exception(f"Failed to fetch playlist: {response.status_code}, {response.text}")
    
    return response.json()  # Return the JSON data

# Use the token obtained earlier
playlist_id = "37i9dQZEVXbNFJfN1Vw8d9"  # Top 50 Hits Spain Playlist ID
token = get_token()  # Retrieve access token using the function you defined

# Fetch playlist data
playlist_data = get_playlist_tracks(token, playlist_id)

# Print or process the playlist data
print(json.dumps(playlist_data, indent=4))  # Print the result in a formatted way

def display_playlist_tracks(playlist_data):
    # Extract the list of tracks from the playlist data
    tracks = playlist_data['tracks']['items']  # Navigate to the tracks list

    for idx, item in enumerate(tracks):
        track = item['track']
        track_name = track['name']  # Track name
        artist_name = ", ".join([artist['name'] for artist in track['artists']])  # Join multiple artists
        album_name = track['album']['name']  # Album name
        
        # Print or format the output
        print(f"{idx+1}. {track_name} by {artist_name} from the album {album_name}")

# Display the tracks
display_playlist_tracks(playlist_data)






