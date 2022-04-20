import json
from hashlib import blake2b
import csv

def queryBuilding(queryKeywords):
    """ This function is used to build a query to send request to the Twitter API.

    :parameter queryKeywords: dictionary for the keywords
    :return: a query that can be used to send request to Twitter API using Tweetpy.
    """
    query = ''
    for orList in queryKeywords['orKeywords']:
        temp = ''
        j=0
        for i in orList:
            if  j != len(orList) - 1 : 
                temp = temp + i + " OR "
            else: 
                temp = temp + i + ""
            j = j + 1  
        if len(orList) > 1 :
            temp = "(" + temp + ")"
        query = query + temp + ' '
    for excluded in queryKeywords['exclude_keywords']:
        query = query + "-" + excluded + " "
    if queryKeywords['withRT']: 
        query =  query + "-is:retweet "
    if queryKeywords['lang']: 
        query = query + f'lang:{queryKeywords["lang"]}'
    return query

# Function to convert a CSV to JSON
# Takes the file paths as arguments
def make_json(csvFilePath, jsonFilePath):
    # create a dictionary
    data = {}

    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        
        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:
    
            # Assuming a column named 'No' to
            # be the primary key
            key = rows['No']
            data[key] = rows

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))

def keywords_to_array(strings):
    result = []
    result = strings[1:len(strings)-1]
    result = result.split(', ')
    return result
# usage
if __name__ == "__main__":
    # querys = queryBuilding('../input/inputfile.json')
    # f = open('../input/providedInput.json')
    # h = blake2b(digest_size=10)
    # topics = json.load(f)
    # result=[]
    # for topic in topics:
    #     # create a hashid with the topic name
    #     topicName = (topic['topic']).encode('UTF-8')
    #     h.update(topicName)
    #     id = h.hexdigest()
    #     # build query 
    #     query = queryBuilding(topic['query'])
    #     result.append({"topicId": id , "topic": topic['topic'], "query": query})
    #     f.close()
    #     # return query with identifier
    # print(result)
    csvFilePath = '../input/providedInput.csv'
    jsonFilePath = '../input/testingInput.json'
    
    # Call the make_json function
    make_json(csvFilePath, jsonFilePath)