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
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np
from requests import post

sia = SentimentIntensityAnalyzer()
current_country="it"

def preprocess_text(text):
    lines = text.splitlines()
    lines.pop(0)  # Remove the first line
    lyrics_cleaned = "\n".join(lines)

    if lyrics_cleaned.endswith("Embed"):
        lyrics_cleaned = lyrics_cleaned[:-5] 

    tokeniser = RegexpTokenizer(r'[A-Za-z]+')
    tokens = tokeniser.tokenize(lyrics_cleaned)
    
    data_token = [token.lower() for token in tokens]
    processed_words = [w for w in data_token if w not in stop_words]
    
    return processed_words

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

pf = pd.DataFrame(pd.read_excel(f"song_lyrics_data_{current_country}.xlsx"))
pf['Lyrics'] = pf['Lyrics'].astype(str)

pf['CleanedLyricsList'] = pf['Lyrics'].apply(preprocess_text)
pf['CleanedLyrics'] = [' '.join(map(str, l)) for l in pf['CleanedLyricsList']]


vader_dataframe=pf
vader_dataframe['scores'] = vader_dataframe['CleanedLyrics'].apply(lambda CleanedLyrics: sia.polarity_scores(CleanedLyrics))

vader_dataframe['compound'] = vader_dataframe['scores'].apply(lambda score_dict: score_dict['compound'])
vader_dataframe['sentiment']=''
vader_dataframe.loc[vader_dataframe.compound>0,'sentiment']='positive'
vader_dataframe.loc[vader_dataframe.compound==0,'sentiment']='neutral'
vader_dataframe.loc[vader_dataframe.compound<0,'sentiment']='negative'
vader_dataframe.to_excel(f"song_lyrics_data_{current_country}_with_scores.xlsx", index=False)
