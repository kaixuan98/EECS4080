====================
Twitter API requests
====================

In this script, it will be performing two task - query building and data requesting. The details of the task will be listed in the following.


Building Query
==============

Input File
----------
The input file to the query is formated in json. The structure of the json is shown below. 

.. code-block:: json

        {"keywords": ["climatechange", "ecofriendly", "sustainable", "zerowaste", "environment", "climateaction", "savetheplanet", "globalwarming"],
        "withRT" : true ,
        "lang": "en",
        "exclude_keywords" : ["RT"]}

``keywords`` are the keywords that need to be include to the query. ``withRT`` is true if the retweet is inlcuded in the query building. ``lang`` specified the language type
of each tweet. The language are formated in ``lang_code``. ``exclude_keywords`` is any keywords that does not want to be included in the search . `

Query Formation
---------------
The input file will be passed into ``queryBuliding`` function to extract all the details and building a query that can used to perform requesting later. 

Requesting Data
===============
After building out the query, it will be used to request tweets from Twitter API. The function will be using tweepy pagination and performing a recent search on Twitter API. 



.. automodule:: twitter_request
    :members:
    :undoc-members:
    :show-inheritance:

