from tweepy import Stream
from tweepy import OAuthHandler
from tweepy import API

from tweepy.streaming import StreamListener
from secretes import Secretes

class TwitterTipBot( StreamListener ):
    auth = None
    api = None
    stream = None

    def __init__( self ):
        try:
            self.auth = OAuthHandler(Secretes._twitterConsumerApiKey, Secretes._twitterConsumerApiSecret)
            self.auth.secure = True
            self.auth.set_access_token(Secretes._twitterAccessToken, Secretes._twitterAccessTokenSecret)
            self.api = API(self.auth)
            self.getLatestMessage()
        except BaseException as e:
            print("Error in main()", e)
        self.tweetCount = 0

    def getLatestMessage(self):
        last_dms = self.api.list_direct_messages()
        for messages in last_dms:
            print(messages)