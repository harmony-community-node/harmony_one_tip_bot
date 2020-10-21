
import tweepy
from tweepy import OAuthHandler
from tweepy import API
from tweepy.streaming import StreamListener
from secretes import Secretes
from time import sleep
from datastore import DataStore
from hmyclient import HmyClient

class TipBotMessageListener(tweepy.StreamListener):
    dataStore = None
    api = None
    bot_twitter_handle = "prarysoft"
    def __init__( self, tApi ):
        super(TipBotMessageListener, self).__init__()
        self.tweetCount = 0
        self.api = tApi
        self.dataStore = DataStore()

    def on_connect( self ):
        print("Connection established!!")

    def on_disconnect( self, notice ):
        print("Connection lost!! : ", notice)
    
    def on_status(self, status):
        receiver = ""
        tip = 0
        success = "yes"
        failure_reason = ""
        tweet_type = "tweet"
        reply_text = ""
        if status.text.startswith(f'@{self.bot_twitter_handle} !tip'):
            if not self.dataStore.checkIftweetDataExists(status.id_str): 
                sender_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{status.user.screen_name}')
                if sender_details != None:
                    parts = status.text.split(" ")
                    for i in range(0, len(parts)):
                        if parts[i] == "!tip":
                            if i + 1 < len(parts):
                                tip = float(parts[i + 1])
                                break
                    if 'user_mentions' in status.entities:
                        for entity in status.entities['user_mentions']:
                            if entity['screen_name'] != self.bot_twitter_handle:
                                receiver = entity['screen_name']
                                break
                    from_address = sender_details['one_address']
                    sender = status.user.screen_name
                    if receiver != "":
                        # Can't tip yourself
                        if sender != receiver:                            				
                            # Can't tip more than you have
                            from_balance = HmyClient.getBalace(from_address)
                            if tip + 0.00000021 > from_balance:
                                reply_text = f'@{status.user.screen_name}, your balance is low to tip {tip} ONE'
                            else:
                                receiver_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{receiver}')
                                if receiver_details == None:
                                    reply_text = f"@{status.user.screen_name}, @{receiver} is not registered with ONE Tipping bot, please register using Telegram bot (https://t.me/onetipbot)"
                                else:
                                    if 'one_address' in receiver_details:
                                        res = HmyClient.transfer(from_address, receiver_details['one_address'], tip)
                                        res = eval(res)
                                        if 'transaction-hash' in res:
                                            reply_text = f"Hi @{receiver}, @{status.user.screen_name} just tipped you {tip} ONE"
                                        else:
                                            print(f"Tip failed from  {sender} to {receiver} tip {tip} ONE")
                                    else:
                                        print('Receiver ONE address is missing')
                        else:
                            reply_text = f'@{status.user.screen_name} You can\'t tip yourself!'
                    else:
                        reply_text = f'@{status.user.screen_name} Please mention a receiver to tip.'
                else:
                    success = "no"
                    failure_reason = "account does not exists"
                    reply_text = f'@{status.user.screen_name} You are not registered with ONE Tipping bot, please register using Telegram bot (https://t.me/onetipbot).'
                if reply_text != "":
                    self.api.update_status(status = reply_text, in_reply_to_status_id = status.id_str)
                    print(reply_text)
                tweetDetails = {
                    'tweet_id' : status.id_str,
                    'sender' : status.user.screen_name,
                    'receiver' : receiver,
                    'tip' : tip,
                    'text' : status.text,
                    'replied' : "yes",
                    'success' : success,
                    'failure_reason' : failure_reason,
                    'tweet_type' : tweet_type,
                    'reply_text' : reply_text
                }
                self.dataStore.saveTweetDetails(tweetDetails)
            else:
                print("Tweet already served")
        else:
            print("Not a Tipping tweet")

    def on_error( self, status ):
        print(status)

class TwitterTipBot():
    auth = None
    api = None
    stream = None
    twitter_uid = "1190625904717959169"

    def __init__( self ):
        try:
            self.auth = OAuthHandler(Secretes._twitterConsumerApiKey, Secretes._twitterConsumerApiSecret)
            self.auth.secure = True
            self.auth.set_access_token(Secretes._twitterAccessToken, Secretes._twitterAccessTokenSecret)
            self.api = API(self.auth)
            tipBotMessageListener = TipBotMessageListener(self.api)
            myStream = tweepy.Stream(auth = self.api.auth, listener=tipBotMessageListener)
            myStream.filter(follow=[self.twitter_uid], is_async=True)
        except BaseException as e:
            print("Error in main()", e)
        self.tweetCount = 0

    def getLatestMessage(self):
        print('Listening to messages')
        while 1:
            try:
                last_dms = tweepy.Cursor(self.api.list_direct_messages).items(20) 
                for messages in last_dms:
                    print("The recipient_id is : " + messages.message_create['target']['recipient_id']) 
                    print("The sender_id is : " + messages.message_create['sender_id']) 
                    print("The text is : " + str(messages.message_create['message_data']['text'])) 
            except Exception as ex:
                print(ex)
            sleep(61)
    
twitterBot = TwitterTipBot()
#twitterBot.getLatestMessage()