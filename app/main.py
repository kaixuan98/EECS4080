from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from os.path import join, dirname, realpath, exists
import sys
import json
from requests import head
from sassutils.wsgi import SassMiddleware
from decouple import config
import tweepy
import pandas as pd
import dateutil.parser as parser
import ntpath
import plotly
import plotly.express as px
import ast
import geopandas as gdp 




app = Flask(__name__)
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'main': ('static/sass', 'static/css', '/static/css')
})


# enable debugging mode
app.config["DEBUG"] = True

# Upload folder
UPLOAD_FOLDER = 'static/files'
OUPUT_DF = 'static/files/output'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
app.config['OUPUT_DF'] =  OUPUT_DF


module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from data_collecting.twitter_request import TweetsReq, requestData, requestUserLocation, chunks
from data_collecting.queryBuilding import queryBuilding, make_json,keywords_to_array
from data_cleaning.data_cleaning import clean_tweet
from translation.google_translate import translate_text

api_key = config('API_KEY')
api_key_secret = config('API_KEY_SECRET')
access_token = config('ACCESS_TOKEN')
access_token_secret = config('ACCESS_TOKEN_SECRET')
bearer_token = config('BEARER_TOKEN')

# Step 0: authenticate
client = tweepy.Client(bearer_token=bearer_token)

# Step 0: Request data with all the parameters needed
COLUMNS = ['tweetId', 'author_id', 'tweet', 'lang', 'created_at']
tweet_fields = ['lang', 'created_at']
expansions = ['author_id']
curr_next_token = ''

# Root URL
@app.route('/')
def index():
    # Set The upload HTML template '\templates\index.html'
    return render_template('index.html', result =[] , len=0)


# Get the uploaded files
@app.route("/", methods=['POST'])
def uploadFiles():
    result =[]
    resultLength = 0
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename) # set the uploaded path
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'testingInput.json') # set the output file path
        uploaded_file.save(file_path) # save the file
        make_json(file_path, output_file) # convert csv to json
        f = open(output_file) # open output file
        inputFile = json.load(f) 
        for topic in inputFile:
            # create a hashid with the topic nam)
            topicName = inputFile.get(topic)['topic']
            id = abs(hash(topicName)) % (10 ** 10)
            # # build query 
            keywords = inputFile.get(topic)['orKeywords'].split(";")
            orKeywords =[]
            for keyword in keywords:
                orKeywords.append(keywords_to_array(keyword))
            lang = inputFile.get(topic)['lang']
            exclude = keywords_to_array(inputFile.get(topic)['excludedKeyword'])
            withRT = inputFile.get(topic)['withRT']
            inputQuery = {"orKeywords": orKeywords , "withRT": withRT, "lang": lang, "exclude_keywords": exclude }
            query = queryBuilding(inputQuery)
            result.append({ "topicId": id , "topic": topicName, "query": query})
        f.close()
        resultLength = len(result)
        queries_file = os.path.join(app.config['UPLOAD_FOLDER'], 'queries.json') # save queries to file
        with open(queries_file, 'w') as queryF:
            json.dump(result, queryF)  
    return render_template("index.html", result = result , len=resultLength )

# collect raw data include user location 
@app.route("/collect", methods=['GET'])
def collect():
    filenames = os.listdir(OUPUT_DF)
    files = []
    for file in filenames: 
        filename = ntpath.basename(file)[:-4]
        if filename.find('with_loc') > 0: 
            files.append(file)
    fileLen = len(files)
    filePath = os.path.join(app.config['OUPUT_DF'], 'raw_data_with_loc.csv')
    df = pd.read_csv(filePath)
    df = df.drop(columns=['author_id_y'])
    df = df.rename(columns={'author_id_x' : 'author_id'})   
    df = df.head()
    return render_template('collect.html', files=files , fileLen=fileLen , tables=[df.to_html(classes='styled-table')], titles=df.columns.values)

@app.route('/collect/<path:filename>')
def download(filename):
    path = os.path.join(app.config['OUPUT_DF'], filename)
    return send_file(path, as_attachment=True)

# here will clean and translate
@app.route("/clean", methods=['GET'])
def cleaning():
    filenames = os.listdir(OUPUT_DF)
    files = []
    for file in filenames: 
        filename = ntpath.basename(file)[:-4]
        if filename.find('location') >= 0: 
            files.append(file)
    fileLen = len(files)
    filePath = os.path.join(app.config['OUPUT_DF'], 'location_user.csv')
    df = pd.read_csv(filePath) 
    df = df.loc[200:205]
    return render_template('clean.html', files=files , fileLen=fileLen , tables=[df.to_html(classes='styled-table')], titles=df.columns.values)

@app.route('/clean/<path:filename>')
def download_clean(filename):
    path = os.path.join(app.config['OUPUT_DF'], filename)
    return send_file(path, as_attachment=True)

# sent to sentiment model and then visualize here
@app.route('/analysis')
def analysis():
    filenames = os.listdir(OUPUT_DF)
    files = []
    for file in filenames: 
        filename = ntpath.basename(file)[:-4]
        if filename.find('clean_data') >= 0: 
            files.append(file)
    filePath = os.path.join(app.config['OUPUT_DF'], 'location_user.csv')
    df = pd.read_csv(filePath)  
    cardiff_label = []
    cardiff_score = []
    result = os.path.join(app.config['OUPUT_DF'], 'cardiff_result.txt')
    with open(result, 'r') as f:
        for line in f:
            line = line.strip()
            data = ast.literal_eval(line)
            if data.get('label') == 'LABEL_0': 
                label = 0
            elif data.get('label') == 'LABEL_1':
                label = 1 
            else:
                label = 2 
            cardiff_label.append(label)
            cardiff_score.append(data.get('score'))
    df['cardiff_label'] = cardiff_label
    df['cardiff_score'] = cardiff_score
    df = df.dropna()
    df['country']= df['country'].apply(lambda x : x.strip() )  
    result = df.groupby(['country','cardiff_label']).size().reset_index(name='count') 
    result.loc[result['country'] == "United States", 'country'] = "United States of America"
    geo_df = gdp.GeoDataFrame.from_file(gdp.datasets.get_path('naturalearth_lowres')).merge(result, left_on='name', right_on='country', how='left').set_index("iso_a3")
    neg_world = geo_df.loc[geo_df['cardiff_label'] == 0]
    neu_world = geo_df.loc[geo_df['cardiff_label'] == 1]
    pos_world = geo_df.loc[geo_df['cardiff_label'] == 2]
    fig = px.choropleth(pos_world, locations=pos_world.index,
                    color="count", # lifeExp is a column of gapminder
                    hover_name="count", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.YlGn)
    fig2 = px.choropleth(neu_world, locations=neu_world.index,
                    color="count", # lifeExp is a column of gapminder
                    hover_name="count", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.YlOrBr)
    fig3 = px.choropleth(neg_world, locations=neg_world.index,
                    color="count", # lifeExp is a column of gapminder
                    hover_name="count", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Reds)
    fig4 = px.histogram(df, x="country", color="cardiff_label", barmode='group')
    top10Lang = (df.groupby(['lang', 'cardiff_label']).size().reset_index(name='count').sort_values(by="count", ascending=False))
    fig5 = px.histogram(top10Lang , x="lang", y='count',color="cardiff_label", barmode="group")
    fig.update_geos(fitbounds="locations", visible=False)
    fig2.update_geos(fitbounds="locations", visible=False)
    fig3.update_geos(fitbounds="locations", visible=False)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) 
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder) 
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder) 
    graphJSON4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder) 
    graphJSON5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder) 
    return render_template('visualize.html', graphJSON=graphJSON, graphJSON2=graphJSON2, graphJSON3=graphJSON3, graphJSON4=graphJSON4, graphJSON5=graphJSON5)

# ========================================= Previous Version with much detailed steps ==============================================
# @app.route("/collect", methods=['GET','POST'])
# def collect():
#     fileLen = 0 
#     if request.method == 'POST':
#         start_date = parser.parse(request.form.get("start"))
#         end_date = parser.parse(request.form.get("end"))
#         queries_file = os.path.join(app.config['UPLOAD_FOLDER'], 'queries.json') # save queries to file
#         f = open(queries_file) # open output file
#         inputFile = json.load(f) 
#         startTime = start_date.isoformat() + "Z"
#         endTime = end_date.isoformat() + "Z"
#         for topic in inputFile:
#             df = requestData(client, topic['query'], COLUMNS, tweet_fields, expansions, startTime, endTime, 100, 100) 
#             # add topic id to the dataframe
#             topicCol = [topic['topicId']] * len(df)
#             topicCol = pd.DataFrame(topicCol , columns=['topic_id'])
#             df = pd.concat([df, topicCol], axis=1)
#             topicName = topic['topic'].replace(" ", '')
#             saveFileName = topicName + '.csv'
#             saveFile = os.path.join(app.config['OUPUT_DF'], saveFileName ) # save queries to file
#             if exists(saveFile):
#                 with open(saveFile, 'r') as f:
#                     header_list = f.readline().strip().split(",")
#                 if header_list.sort() == COLUMNS.copy().sort(): 
#                     df.to_csv(saveFile, index=False , header=False, mode='a')
#                 else: 
#                     df.to_csv(saveFile, index=False)
#             else:
#                 df.to_csv(saveFile, index=False)
#         filenames = os.listdir(OUPUT_DF)
#         fileLen = len(filenames)
#         return render_template('collect.html', files=filenames , fileLen=fileLen)
#     else: 
#         filenames = os.listdir(OUPUT_DF)
#         fileLen = len(filenames)
#         return render_template('collect.html', files=filenames , fileLen=fileLen)

# @app.route("/users", methods=['GET'])
# def users():
#     files = os.listdir(OUPUT_DF)
#     for file in files: 
#         path = os.path.join(app.config['OUPUT_DF'], file)
#         f = open(path)
#         filename = ntpath.basename(path)[:-4]
#         saveFile = filename + '_withLoc.csv'
#         saveFile_path = os.path.join(app.config['OUPUT_DF'], saveFile) 
#         tweet_df = pd.read_csv(f)
#         tweet_df = tweet_df.dropna()
#         batches = list(chunks(list(tweet_df['author_id']), 100))
#         tweetID_batches = list(chunks(list(tweet_df['tweetId']), 100))
#         loc_list = requestUserLocation(client, batches, tweetID_batches)
#         location_df = pd.DataFrame(loc_list)  
#         full_df = pd.merge(tweet_df, location_df , on="tweetId")
#         full_df.to_csv(saveFile_path)
#     filenames = os.listdir(OUPUT_DF)
#     fileLen = len(filenames)
#     return render_template('users.html' , files=filenames, fileLen=fileLen)

# @app.route('/users/<path:filename>')
# def download_user(filename):
#     path = os.path.join(app.config['OUPUT_DF'], filename)
#     return send_file(path, as_attachment=True)

# @app.route("/clean", methods=['GET'])
# def cleaning():
#     files = os.listdir(OUPUT_DF)
#     for file in files: 
#         path = os.path.join(app.config['OUPUT_DF'], file)
#         f = open(path)
#         filename = ntpath.basename(path)[:-4]
#         if filename.find("withLoc") > 0 :
#             saveFile = filename + '_basic_clean.csv'
#             saveFile_path = os.path.join(app.config['OUPUT_DF'], saveFile) 
#             full_df = pd.read_csv(f)
#             full_df['clean_tweet'] = [clean_tweet(tw) for tw in full_df['tweet']]
#             full_df.to_csv(saveFile_path)
#     filenames = os.listdir(OUPUT_DF)
#     fileLen = len(filenames)
#     return render_template('clean.html', files=filenames, fileLen=fileLen)

# @app.route('/clean/<path:filename>')
# def download_clean(filename):
#     path = os.path.join(app.config['OUPUT_DF'], filename)
#     return send_file(path, as_attachment=True)

# @app.route("/translate", methods=['GET'])
# def translate():
#     files = os.listdir(OUPUT_DF)
#     for file in files: 
#         path = os.path.join(app.config['OUPUT_DF'], file)
#         f = open(path)
#         filename = ntpath.basename(path)[:-4]
#         if filename.find("withLoc_basic_clean") > 0 :
#             saveFile = filename + '_translate.csv'
#             saveFile_path = os.path.join(app.config['OUPUT_DF'], saveFile) 
#             full_df = pd.read_csv(f)
#             # for tw in full_df['clean_tweet']:
#             #     translate_text('en', tw)
#             full_df['translated_tweet'] = [translate_text('en', tw) for tw in full_df['clean_tweet']]
#             full_df.to_csv(saveFile_path)
#     filenames = os.listdir(OUPUT_DF)
#     fileLen = len(filenames)
#     return render_template('translate.html', files=filenames, fileLen=fileLen)


# @app.route('/translate/<path:filename>')
# def download_translate(filename):
#     path = os.path.join(app.config['OUPUT_DF'], filename)
#     return send_file(path, as_attachment=True)

if (__name__ == "__main__"):
    app.run(port = 5000)