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
from textblob import TextBlob


sia = SentimentIntensityAnalyzer()
current_country="br"

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
stop_words_en.extend([
       'oh', 'yeah', 'woo', 'ah', 'ooh', 'whoa', 'la', 'na', 'nah', 'da', 
    'doo', 'hey', 'ha', 'ho', 'uh', 'ye', 'ay', 'ayyy', 'woah', 'hmm', 
    'mmm', 'bam', 'shoo', 'laa', 'du', 'di', 'ba', 'whoo', 'yo', 'yay', 
    'yup', 'mmm', 'uh-huh', 'alright', 'c’mon', 'woop', 'doo-wop', 'uh-oh', 
    'aye', 'nah-nah','or', 'm', 'ma', 'ours', 'against', 'nor', "it's", 'o', 
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
stop_words_es.extend([    
    'algo', 'algunos', 'ambos', 'ante', 'aquel', 'aquellos', 'aquél', 'aquí', 'así', 
    'cada', 'casi', 'cierta', 'ciertos', 'conmigo', 'contigo', 'demasiado', 'demás', 
    'desde', 'donde', 'durante', 'entre', 'era', 'eras', 'éramos', 'está', 'están', 
    'estás', 'este', 'estos', 'existe', 'existen', 'fue', 'fuera', 'fueron', 'había', 
    'hubo', 'incluso', 'intenta', 'intentas', 'intento', 'jamás', 'largo', 'luego', 
    'más', 'mientras', 'mismo', 'muchos', 'ninguna', 'ninguno', 'otra', 'otros', 'podía', 
    'podrían', 'podríamos', 'posible', 'puede', 'pueden', 'quedó', 'siempre', 'siendo', 
    'tal', 'tales', 'tanto', 'todavía', 'trabaja', 'tuyo', 'usted', 'vosotros'
    ])
stop_words_su=stopwords.words('swedish')
stop_words_su.extend([
        'alltså', 'andra', 'bara', 'behöver', 'bland', 'blir', 'bort', 'därefter', 'dess', 
    'dock', 'efteråt', 'egen', 'enligt', 'er', 'fram', 'framför', 'genom', 'gör', 'hela', 
    'här', 'ibland', 'inget', 'innan', 'inte', 'just', 'kanske', 'kan', 'kommer', 'liknande', 
    'medan', 'mer', 'mindre', 'någon', 'något', 'nån', 'några', 'nästa', 'också', 'omkring', 
    'senare', 'skulle', 'sådan', 'sådant', 'sådär', 'tills', 'trots', 'ungefär', 'utom', 
    'vad', 'vilka', 'vilken', 'vilket'
])
stop_words_it=stopwords.words('italian')
stop_words_it.extend([
        'abbastanza', 'alcuni', 'altro', 'ancora', 'anche', 'ben', 'bisogna', 'cioè', 
    'così', 'di', 'dopo', 'durante', 'ecco', 'essere', 'facciamo', 'fare', 'fatto', 
    'finché', 'già', 'grande', 'ieri', 'inoltre', 'insieme', 'lontano', 'mai', 
    'magari', 'molti', 'nessuna', 'nessuno', 'nonostante', 'nostra', 'nostri', 
    'ogni', 'ormai', 'però', 'piuttosto', 'poco', 'proprio', 'quale', 'qualunque', 
    'quanto', 'questi', 'sarà', 'sotto', 'stavolta', 'suo', 'sulla', 'troppo', 
    'tua', 'tuo', 'verso', 'vostro'
])
stop_words_po=stopwords.words('portuguese')

stop_words = [*stop_words_en,*stop_words_es,*stop_words_it,*stop_words_su,*stop_words_po]

pf = pd.DataFrame(pd.read_excel(f"song_lyrics_data_{current_country}.xlsx"))
pf['Lyrics'] = pf['Lyrics'].astype(str)

pf['CleanedLyricsList'] = pf['Lyrics'].apply(preprocess_text)
pf['CleanedLyrics'] = [' '.join(map(str, l)) for l in pf['CleanedLyricsList']]

"""
vader_dataframe=pf
vader_dataframe['scores'] = vader_dataframe['CleanedLyrics'].apply(lambda CleanedLyrics: sia.polarity_scores(CleanedLyrics))

vader_dataframe['positive'] = vader_dataframe['scores'].apply(lambda score_dict: score_dict['pos'])
vader_dataframe['neutral'] = vader_dataframe['scores'].apply(lambda score_dict: score_dict['neu'])
vader_dataframe['negative'] = vader_dataframe['scores'].apply(lambda score_dict: score_dict['neg'])
vader_dataframe['compound'] = vader_dataframe['scores'].apply(lambda score_dict: score_dict['compound'])
vader_dataframe['sentiment']=''
vader_dataframe.loc[vader_dataframe.compound>0,'sentiment']='positive'
vader_dataframe.loc[vader_dataframe.compound==0,'sentiment']='neutral'
vader_dataframe.loc[vader_dataframe.compound<0,'sentiment']='negative'
#vader_dataframe.to_excel(f"song_lyrics_data_{current_country}_with_scores.xlsx", index=False)

blob_dataframe_clean=pf
blob_dataframe_clean['scores'] = blob_dataframe_clean['CleanedLyrics'].apply(lambda CleanedLyrics: TextBlob(CleanedLyrics).sentiment)
blob_dataframe_clean['polarity']=blob_dataframe_clean['scores'].str.get(0)
blob_dataframe_clean['subjectivity']=blob_dataframe_clean['scores'].str.get(1)
blob_dataframe_clean['sentiment']=''
blob_dataframe_clean.loc[blob_dataframe_clean.polarity>0,'sentiment']='positive'
blob_dataframe_clean.loc[blob_dataframe_clean.polarity==0,'sentiment']='neutral'
blob_dataframe_clean.loc[blob_dataframe_clean.polarity<0,'sentiment']='negative'
#blob_dataframe_clean.to_excel(f"song_lyrics_data_{current_country}_with_scores_textblob.xlsx", index=False)
"""

joint_dataframe = pf

# Vader analysis
joint_dataframe['scores_vader'] = joint_dataframe['CleanedLyrics'].apply(lambda CleanedLyrics: sia.polarity_scores(CleanedLyrics))
joint_dataframe['positive_vader'] = joint_dataframe['scores_vader'].apply(lambda score_dict: score_dict['pos'])
joint_dataframe['neutral_vader'] = joint_dataframe['scores_vader'].apply(lambda score_dict: score_dict['neu'])
joint_dataframe['negative_vader'] = joint_dataframe['scores_vader'].apply(lambda score_dict: score_dict['neg'])
joint_dataframe['compound_vader'] = joint_dataframe['scores_vader'].apply(lambda score_dict: score_dict['compound'])


joint_dataframe['sentiment_vader']=''
joint_dataframe.loc[joint_dataframe.compound_vader>0,'sentiment_vader']='positive'
joint_dataframe.loc[joint_dataframe.compound_vader==0,'sentiment_vader']='neutral'
joint_dataframe.loc[joint_dataframe.compound_vader<0,'sentiment_vader']='negative'

joint_dataframe['scores_textblob'] = joint_dataframe['CleanedLyrics'].apply(lambda CleanedLyrics: TextBlob(CleanedLyrics).sentiment)
joint_dataframe['polarity_textblob']=joint_dataframe['scores_textblob'].str.get(0)
joint_dataframe['subjectivity_textblob']=joint_dataframe['scores_textblob'].str.get(1)
joint_dataframe['sentiment_textblob']=''
joint_dataframe.loc[joint_dataframe.polarity_textblob>0,'sentiment_textblob']='positive'
joint_dataframe.loc[joint_dataframe.polarity_textblob==0,'sentiment_textblob']='neutral'
joint_dataframe.loc[joint_dataframe.polarity_textblob<0,'sentimen_textblob']='negative'

joint_dataframe.to_excel(f"song_lyrics_data_{current_country}_with_scores.xlsx", index=False)