""" this is a mixture of the best #free twitter sentimentanalysis modules on github.
    i took the most usable codes and mixed them into one because all of them
    where for a linguistical search not usable and did not show a retweet or a full tweet
    no output as csv, only few informations of a tweet, switching language
    or even to compare linguistic features in tweets of two different langauges and etc. etc ...
    special and many many thanks to https://github.com/vprusso/youtube_tutorials who showed on his
    page a tutorial on how to do a sentimentanalysis with python
    i did this for users with not much skills and linguistical background to help them to get a corpus of twitterdata
    and to show them how to do a comparison between sentence based vs document based sentimentanalysis
    credits to all AVAILABLE FREE AND SIMPLE sentimentanalysis programms (dec. 2019) on github.
    many thanks to everybody and of course to github for making this exchange and usage possible!
    cemre koc (Goethe University, Frankfurt) Python3.7
"""

from textblob import TextBlob   #Sentimentlexikon FOR GERMAN (TEXTBLOB_DE import textblob_de
import re                       #modul for regular expressions

from tweepy import API                      #Twitter API modul for more info: look tweepy doc please!
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import tweepy                           #usage of diffrent feautres of my programm
import sys                              #only if wanted
import csv                              ##only if wanted (see rest of programm)
import pandas as pd                     #pandas for illustration
import authentification                 #access to twitter
import numpy as np                      #collection of tweets via numpy
import matplotlib.pyplot as plt         #if needed (see below for ploting)
import numpy

#output screen (if you use pycharm for full screen view)
#only if needed
pd.set_option('display.max_rows', 1000000000000)
pd.set_option('display.max_columns', 1000000000)
pd.set_option('display.width', 100000000000)
pd.set_option('display.float_format', '{:20,.2f}'.format)

#for maximal OUTPUT!
#pd.set_option('display.max_colwidth', -1)



#TWITTER AUTHENTIFICTION (Twitter development)
#please fill for that the identification.py with your credentials!
#you need a twitter developer account for getting these informations
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(authentification.CONSUMER_KEY, authentification.CONSUMER_SECRET)
        auth.set_access_token(authentification.ACCESS_TOKEN, authentification.ACCESS_TOKEN_SECRET)
        return auth


#TWITTER CLIENT SERVER
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user


    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


#TWITTER STREAMER FOR STREAMING AND LIVE TWEETS
class TwitterStreamer():

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()    

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # AUTHENTIFICATION AND CONNECTION TO API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)

        #you can use the stream.filter for defining the search for words/hasthags!!!!!!
        #same sentimentanalysis works for words or hashtags!!!
        stream.filter(track=hash_tag_list)


#TWITTER STREAM LISTENER FOR PRINTING TWEETS
class TwitterListener(StreamListener):


    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            #OCCURS IF RATE LIMIT IS PASSED
            return False
        print(status)

#FOR ANALYZING CLEANING TWEETS (TO CONTENT)
class TweetAnalyzer():
#DELTETE ALL UNNECESSARY CHARACTERS
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

#SIMPLE SENTIMENTANALYSIS VIA TEXTBLOB (englisch)
    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
#You can use the following classification of polarity for sentence based analysis
#since i am using this programm for document level classification I left it with 1 -1  and 0
#       if (polarity == 0):
#            print("Neutral")
#     elif (polarity > 0 and polarity <= 0.3):
#            print("Schwach positiv")
#        elif (polarity > 0.3 and polarity <= 0.6):
#            print("positiv")
#        elif (polarity > 0.6 and polarity <= 1.0):
#            print("Stark positiv")
#        elif (polarity > -0.3 and polarity <= 0):
#            print("schwach negativ")
#        elif (polarity > -0.6 and polarity <= -0.3):
#            print("Negativ")
#        elif (polarity >= -1.0 and polarity <= -0.6):
#            print("Stark negativ")

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.full_text for tweet in tweets], columns=['tweets'])
#THIS IS FOR RETWEETS OF A CERTAIN TWEET! BUT BE CARFUL ONLY A CERTAIN NUMBER OF TWEETS PER DAY!
#TWITTER RESTRICTION
#remove the """ for usage!

        """replies = []
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        for full_tweets in tweepy.Cursor(api.user_timeline, screen_name='GretaThunberg', timeout=999999).items(20):
            for tweet in tweepy.Cursor(api.search, q='to:GretaThunberg', since_id=1203618558267273225,
                                       result_type='recent',
                                       timeout=999999).items(100):
                if hasattr(tweet, 'in_reply_to_status_id_str'):
                    if (tweet.in_reply_to_status_id_str == full_tweets.id_str):
                        replies.append(tweet.text)
            print("Tweet :", full_tweets.text.translate(non_bmp_map))
            for elements in replies:
                print("Replies :", elements)
            # replies.clear()"""

#DATA SET VIA DATAFRAME TO SHOW WITH NUMPY
#YOU CAN PRINT GIVEN DATA LIKE LENGTH RETWEET NUMBER LANGUAGE etc. CHOSSE:

#['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__',
# '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '_
# _lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '_
# _sizeof__', '__str__', '__subclasshook__', '__weakref__', '_api', '_json', 'author', 'contributors', 'coordinates',
# 'created_at', 'destroy', 'display_text_range', 'entities', 'favorite', 'favorite_count', 'favorited',
# 'full_text', 'geo', 'id', 'id_str', 'in_reply_to_screen_name', 'in_reply_to_status_id', 'in_reply_to_status_id_str',
# 'in_reply_to_user_id', 'in_reply_to_user_id_str', 'is_quote_status', 'lang', 'parse', 'parse_list', 'place',
# 'possibly_sensitive', 'quoted_status', 'quoted_status_id', 'quoted_status_id_str', 'quoted_status_permalink',
# 'retweet', 'retweet_count', 'retweeted', 'retweets', 'source', 'source_url', 'truncated', 'user']

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.full_text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        #df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df["lang"] = ([tweet.lang for tweet in tweets])
        #df["in_reply_to_status_id_str"] = ([tweet.replies for tweet in tweets])

        return df


#Programm begins here!!

if __name__ == '__main__':

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()
    #TWEET MODE EXTENDED FOR FULL TWEET OUTPUT!! RETWEETS STAY THE SAME!
    #COUNT= LAST TWEET NUMBER OF USER (SCREEN NAME)
    #HERE FOR GRETA THUNBERG, JUST DELETE AND TYPE ACCOUNT NAME TO CHANGE
    #FOR EXAMPLE rtErdogan (for president of turkey), realDonaldTrump (for Trump) etc...
    tweets = api.user_timeline(screen_name="GretaThunberg", count=200, tweet_mode="extended")

    #print DATA
    print(dir(tweets[0]))
    #print(tweets[0].retweet_count)  #retweet count print
    #sentimentanalysis for printing it in a dataframe with the other informations!
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])


    #AVARAGE LENGTH OF ALL TWEETS
    #print(np.mean(df['len']))

    # GET NUMBER OF LIKES
    #print(np.max(df['likes']))

    # GET NUMBER OF RETWEETS
    #print(np.max(df['retweets']))

    #EXAMPLE RETWEET STATUS OF A CERTAIN TWEET ID
    #To get ID you need to look on your broswers URL of this CERTAIN TWEET
    #print(np.max(df["lang"]))
    ##print(df.in_reply_to_status_id[1075801005504258061])

    #ANYWAY THERE IS A RESTRICTION SINCE 2019 ON ONLY 200 TWEETS
    #THANK YOU CAMBRIDGE ANALYTICA
    print(df.head(200))

    #    DO CSV FILE (DELETE OR NAME IT NEW TO MAKE IT SEPRATE)
    #df.to_csv('KocSentiment.csv')

    #TIME SERIES FOR CHART VIEW!!! DONT FORGET TO TURN ON MATPLOT LIBRARY
    #time_likes = pd.Series(data=df['len'].values, index=df['date'])
    #time_likes.plot(figsize=(16, 4), color='r')
    #plt.show()
    
    #time_favs = pd.Series(data=df['likes'].values, index=df['date'])
    #time_favs.plot(figsize=(16, 4), color='r')
    #plt.show()

    #time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    #time_retweets.plot(figsize=(16, 4), color='r')
    #plt.show()

    #LAYERED VIEW! FOR COMPARISON !!
    #time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    #time_likes.plot(figsize=(16, 4), label="likes", legend=True)

    #time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    #time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)
    #plt.show()


