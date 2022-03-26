import json
from hashlib import blake2b

def queryBuilding(queryKeywords):
    """ This function is used to build a query to send request to the Twitter API.

    :parameter queryKeywords: dictionary for the keywords
    :return: a query that can be used to send request to Twitter API using Tweetpy.
    """
    query = ''
    j=0
    for i in queryKeywords['orKeywords']:
        if  j != len(queryKeywords['orKeywords']) - 1 : 
            query = query + i + " OR "
        else: 
            query = query + i + " "
        j = j + 1  
    if queryKeywords['withRT']: 
        query = "(" + query + "-RT) -is:retweet "
    if queryKeywords['lang']: 
        query = query + f'lang:{queryKeywords["lang"]}'
    return query

# usage
if __name__ == "__main__":
    # querys = queryBuilding('../input/inputfile.json')
    f = open('../input/topics.json')
    h = blake2b(digest_size=10)
    topics = json.load(f)
    result=[]
    for topic in topics:
        # create a hashid with the topic name
        topicName = (topic['topic']).encode('UTF-8')
        h.update(topicName)
        id = h.hexdigest()
        # build query 
        query = queryBuilding(topic['query'])
        result.append({"topicId": id , "topic": topic['topic'], "query": query})
        f.close()
        # return query with identifier
    print(result)
        