import pandas as pd
import re
import html
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import datetime

nlp = spacy.load("en_core_web_sm")

def clean_tweet(tweet, lang):
    """ Remove twitter handle, links , digits, puntuation, hashtag and stop words. The stop words are from NLTK library and stop words can be remove based on language.

    :parameter tweet: a tweet
    :parameter lang: language code, currently only support English (en), Spanish(es), and German(de)
    :return: string 
    """
    if lang == 'en':
        stop_words = set(stopwords.words('english'))
    elif lang == 'es':
        stop_words = set(stopwords.words('spanish'))
    elif lang == 'de':
        stop_words = set(stopwords.words('german'))
    temp = tweet.lower()
    temp = temp.replace('\n', ' ')
    temp = html.unescape(temp)
    temp = re.sub("'", "", temp) # to avoid removing contractions in english
    temp = re.sub("@[A-Za-z0-9_]+","", temp)  # removing handle 
    temp = re.sub("#","", temp)  # removing hastags
    temp = re.sub(r'http\S+', '', temp) # removing any link
    temp = re.sub(r'[^\w\s]', ' ', temp)  # remove the punct 
    temp = re.sub('\[.*?\]',' ', temp)  # remove any weird symbol
    temp = re.sub("[^a-z0-9]"," ", temp) # remove any numbers
    print(temp)
    temp = word_tokenize(temp)
    print(temp)
    temp = [w for w in temp if not w.lower() in stop_words]
    temp = " ".join(word for word in temp)
    return temp

def deEmojify(text):
    """ Remove emoji from a text.

    :parameter text: a string
    :return: string 
    """
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def isLocation(doc):
    """ Use Spacy to recognize location for a doc

    :parameter doc: string
    :return: string - the location in the doc 
    """
    result = ''
    doc = nlp(doc)
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            result = ent.text  
    return result

def getLocation(df):
    """ Use geopy to request for the location based on the extracted location

    :parameter df: dataframe 
    :return: df - dataframe with Country name, latitude and longitude
    """
    geolocator = Nominatim(user_agent="my-app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3)
    for i, row in df.iterrows():
        try:
            temp = geocode( (df.loc[i,'extracted_user_loc']) , language='en')
            df.loc[i, 'latitute'] = temp.latitude
            df.loc[i, 'longitute'] = temp.longitude
            df.loc[i, 'country'] = temp[0].split(",")[-1]
            print(i)
        except:
            pass
    return df

if __name__ == "__main__":
    # ASK: should we translate before cleaning or vice versa? 
    tweet = '@GrueneBundestag @cem_oezdemir Eine #Landwirtschaft muss ein Land vor allen Dingen JEDERZEIT autark mit #Obst #Gemüse #Getreide #Fleisch versorgen können Soweit wie möglich #Bio! In #Deutschland wird das nicht gelingen wenn tausende Hektar #Ackerfläche &amp; #Weideland durch #ErneuerbareEnergien vernichtet werden'
    eng_tweet = "@GrueneBundestag @cem_oezdemir An #agriculture must be able to supply a country above all EVERY TIME self-sufficiently with #fruit #vegetables #grain #meat As far as possible #organic! In #Germany this will not succeed if thousands of hectares of #arable land & pasture are destroyed by #renewableenergies."
    tweet2 = "@RealOilRspctr @SeedOilDsrspctr I just saw this organic, OIL FREE oat milk in the store today. For people are intent on drinking oat milk - try MALK. https://t.co/EileDW3v0Y"
    result = clean_tweet(tweet, "de")
    print(result)
    result2 = clean_tweet(tweet2, "en")
    print(result2)