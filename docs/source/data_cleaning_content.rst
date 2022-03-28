==================
Data Preprocessing
==================
In this phase we will be doing some basic cleaning of the tweets that we had collected. 

Cleaning tweets
===============
``clean_tweet`` is used to clean the raw tweets that were collected in the previous phase. Items will be removed is shown in the following list

  * New line will be remove from the tweets to make it as a compelete sentences. 
  * Twitter handles (ie @username) will be remove in this process.
  * Any URL or links that is not important to the analysis. 
  * Punctuations 
  * Numbers or Digits
  * Hashtags

    * the content of hashtag will not be remove because it could be a word that user used to express their content.
    * if the hashtag content has an underscore, it will still be remove after the punctuations
    * since hashtag does not allow spaces, even removing just the hashtag, we are not able to identify is it a word or a phase.

  * Stop words 
    * The stop words are removed based the stop words that provided in NLTK 
    * language will be identify before cleaning and will clean based on the languages
    * currently only support English(en), German(de), and Spanish(es).

Example of the raw tweet: 
::
        "@RealOilRspctr @SeedOilDsrspctr I just saw this organic, OIL FREE oat milk in the store today. For people are intent on drinking oat milk - try MALK. https://t.co/EileDW3v0Y"

Example of clean tweet:
:: 
        saw organic oil free oat milk store today people intent drinking oat milk try malk

Extract User Location
=====================
Due to limited access of Twitter API, the location of the tweets is not accessible. Thus we need to used the user location based on their profile.
This is information is collected in previous data collecting phase. The data that we got suffer from 2 problems. First, most of the user will not declare their location, 
thus the data that we had collected contains a lot of null or empty value. Second, the even user declare their location, creativity will get in the way that user might declare a vauge location, for example - metaverse, in my bed. 

Cleaning and extracting User location

  * Remove the emoji with ``deEmojify``
  * Remove all the null values
  * ``isLocation`` is used to identify an actual location (entity recognition using Spacy)
  * ``getLocation`` is used to request to the coordinates and the country name of the location (Geopositioning with GeoPy)


Functions
=========
.. automodule:: data_cleaning
        :members:
        :undoc-members:
        :show-inheritance:
