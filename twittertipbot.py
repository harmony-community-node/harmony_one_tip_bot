
import tweepy
from tweepy import OAuthHandler
from tweepy import API
from secretes import Secretes
from time import sleep
from datastore import DataStore
from hmyclient import HmyClient
import subprocess

class TwitterTipBot():
    auth = None
    api = None
    stream = None
    twitter_uid = "1190625904717959169"
    bot_twitter_handle = "prarysoft"
    dataStore = None

    def __init__( self ):
        try:
            self.auth = OAuthHandler(Secretes._twitterConsumerApiKey, Secretes._twitterConsumerApiSecret)
            self.auth.secure = True
            self.auth.set_access_token(Secretes._twitterAccessToken, Secretes._twitterAccessTokenSecret)
            self.api = API(self.auth)
            self.dataStore = DataStore()
        except BaseException as e:
            print("Error in main()", e)
        self.tweetCount = 0

    def startTwitterTipBot(self):
        while 1:
            try:
                twitter_event_details = self.dataStore.getNotAddressedTwitterEvents()
                text = twitter_event_details['event_text']
                print(twitter_event_details)
                if text.startswith(f'@{self.bot_twitter_handle} !tip'):
                    self.process_tip(twitter_event_details['event_id'], text, twitter_event_details['sender_handle'], twitter_event_details['receiver_handle'])
                    break
            except Exception as ex:
                print(ex)
            sleep(5)
            
    def process_tip(self, tweet_id, text, sender_handle, receiver):
        tip = 0
        success = "yes"
        failure_reason = ""
        tweet_type = "tweet"
        reply_text = ""
        if text.startswith(f'@{self.bot_twitter_handle} !tip'):
            if not self.dataStore.checkIftweetDataExists(tweet_id): 
                sender_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{sender_handle}')
                if sender_details != None:
                    parts = text.split(" ")
                    for i in range(0, len(parts)):
                        if parts[i] == "!tip":
                            if i + 1 < len(parts):
                                tip = float(parts[i + 1])
                                break
                    from_address = sender_details['one_address']
                    sender = sender_handle
                    if receiver != "":
                        # Can't tip yourself
                        if sender != receiver:                            				
                            # Can't tip more than you have
                            from_balance = HmyClient.getBalace(from_address)
                            if tip + 0.00000021 > from_balance:
                                reply_text = f'@{sender_handle}, your balance is low to tip {tip} ONE'
                            else:
                                receiver_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{receiver}')
                                if receiver_details == None:
                                    reply_text = f"@{sender_handle}, @{receiver} is not registered with ONE Tipping bot, please register using Telegram bot (https://t.me/onetipbot)"
                                else:
                                    if 'one_address' in receiver_details:
                                        res = HmyClient.transfer(from_address, receiver_details['one_address'], tip)
                                        res = eval(res)
                                        if 'transaction-hash' in res:
                                            reply_text = f"Hi @{receiver}, @{sender_handle} just tipped you {tip} ONE"
                                        else:
                                            print(f"Tip failed from  {sender} to {receiver} tip {tip} ONE")
                                    else:
                                        print('Receiver ONE address is missing')
                        else:
                            reply_text = f'@{sender_handle} You can\'t tip yourself!'
                    else:
                        reply_text = f'@{sender_handle} Please mention a receiver to tip.'
                else:
                    success = "no"
                    failure_reason = "account does not exists"
                    reply_text = f'@{sender_handle} You are not registered with ONE Tipping bot, please register using Telegram bot (https://t.me/onetipbot).'
                if reply_text != "":
                    self.api.update_status(status = reply_text, in_reply_to_status_id = tweet_id)
                    print(reply_text)
                tweetDetails = {
                    'tweet_id' : tweet_id,
                    'sender' : sender_handle,
                    'receiver' : receiver,
                    'tip' : tip,
                    'text' : text,
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
    
twitterBot = TwitterTipBot()
twitterBot.startTwitterTipBot()
