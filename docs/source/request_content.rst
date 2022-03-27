===============
Data Collecting
===============

In this script, it will be performing two task - query building and data requesting. The details of the task will be listed in the following.

Input File
==============
The input file is an array of json object. Each json object will be used to build one query and the structure of each object is show in the following

.. code-block:: json

        {
                "topic": "climate change",
                "query" : {
                        "orKeywords": [
                                ["environment", "climate action"],
                                ["ecofriendly", "recycling", "zero waste"]
                        ],
                        "withRT" : true ,
                        "lang": "en",
                        "exclude_keywords" : ["RT"]
                }
        }

``orKeywords`` are list of of arrays. Each of the list will be combine with ``OR``.  For example. the above or keywords will be ``(environment OR climate action) (ecofriendly OR recycling OR zero waste")``.  
``withRT`` is true if the retweet is inlcuded in the query building.  
``lang`` specified the language type of each tweet. The language are formated in ``lang_code``.  
``exclude_keywords`` is any keywords that does not want to be included in the search.   

Building Query
==============
The input file is an array of json object that will be used to build the query. Each of the json object will be passed into ``queryBuilding`` function to extract all the details and building a query that can used to perform requesting later.
In each json object, it consists of the name of the topic, encoding will be performed on the ``topic`` to create a unqiue 10 digit hashed topic id.
The topic id with the built query will then be saved.

.. code-block:: json

        {
                "topicId" : "9715149228",
                "topic" : "climate change",
                "query" : "(environment OR climate action) (ecofriendly OR recycling OR zero waste)"
        }



Requesting Data
===============
After bulding the query, we can the data collecting process. There is 2 main steps in this step, which are
        - the used of ``TweetsReq`` or ``requestData`` function to request tweets
        - the used of ``requestUserLocation`` function to request user location of each tweets

Functions
=========
.. automodule:: queryBuilding
        :members:
        :undoc-members:
        :show-inheritance:

.. automodule:: twitter_request
        :members:
        :undoc-members:
        :show-inheritance:



