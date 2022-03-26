====================
Twitter API requests
====================

In this script, it will be performing two task - query building and data requesting. The details of the task will be listed in the following.

Input File
----------
The input file is an array of json object. Each json object will be used to build one query and the structure of each object is show in the following

.. code-block:: json

        {
        "topic": "climate change",
        "query" : {
                "orKeywords": [
                        hange", "ecofriendly", "recycling", "zero waste", "environment", "climate action", "save the planet", "global warming"
                ],
                "andKeywords": [],
                "withRT" : true ,
                "lang": "en",
                "exclude_keywords" : ["RT"]
        }

``orKeywords`` are the keywords that need to be include to the query. 
``withRT`` is true if the retweet is inlcuded in the query building. 
``lang`` specified the language type of each tweet. The language are formated in ``lang_code``. 
``exclude_keywords`` is any keywords that does not want to be included in the search . 

Building Query
==============

Query Formation
---------------
The input file will be passed into ``queryBuilding`` function to extract all the details and building a query that can used to perform requesting later. 

Requesting Data
===============
After building out the query, it will be used to request tweets from Twitter API. The function will be using tweepy pagination and performing a recent search on Twitter API. 



.. automodule:: twitter_request
        :members:
        :undoc-members:
        :show-inheritance:


.. automodule:: queryBuilding
        :members:
        :undoc-members:
        :show-inheritance:


