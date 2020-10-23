import pymongo
from pymongo import MongoClient

class DataStore:

    client = None
    db = None
    usersData = u'usersData'
    tweetData = u'tweetData'
    twitter_events = u'twitter_events'

    def __init__(self):   
        self.client = MongoClient()
        self.db = self.client.one_tip_bot_data
    
    def checkIfUserRecordExists(self, chat_id, telegram_user_id):
        userDataCollection = self.db.usersData
        doc_ref = userDataCollection.find({"$and":[{'chat_id' : chat_id}, {'telegram_user_id': telegram_user_id}]})
        if doc_ref.count() > 0:
            return True
        else:
            return False
    def checkIfUserRecordExistsWithTwitter(self, twitter_handle):
        userDataCollection = self.db.usersData
        doc_ref = userDataCollection.find({'twitter_handle': twitter_handle})
        if doc_ref.count() > 0:
            return True
        else:
            return False            

    def saveUserDetails(self, userDetails):
        if 'chat_id' in userDetails and 'telegram_user_id' in userDetails:
            userDataCollection = self.db.usersData
            doc_ref = userDataCollection.find({"$and":[{'chat_id' : userDetails['chat_id']}, {'telegram_user_id': userDetails['telegram_user_id']}]})
            if doc_ref.count() == 0:
                #print(f" add {addressData}")
                userDataCollection.insert_one(userDetails)
            else:
                #print(f"update {addressData}")
                userDataCollection.update({ "$and" : [{'chat_id' : userDetails['chat_id']}, {'telegram_user_id': userDetails['telegram_user_id']}]}, userDetails)

    def getUserDetails(self, chat_id, telegram_user_id):
        userDataCollection = self.db.usersData
        doc_ref = userDataCollection.find({"$and":[{'chat_id' : chat_id}, {'telegram_user_id': telegram_user_id}]})
        if doc_ref.count() == 0:
            return None
        else:
            return doc_ref[0]
    
    def getUserDetailsByTwitterHandle(self, twitter_handle):
        userDataCollection = self.db.usersData
        doc_ref = userDataCollection.find({'twitter_handle': twitter_handle})
        if doc_ref.count() == 0:
            return None
        else:
            return doc_ref[0]
    
    def checkIftweetDataExists(self, tweet_id):
        tweetDataCollection = self.db.tweetData
        doc_ref = tweetDataCollection.find({'tweet_id': tweet_id})
        if doc_ref.count() > 0:
            return True
        else:
            return False

    def getTweetDetails(self, tweet_id):
        tweetDataCollection = self.db.tweetData
        doc_ref = tweetDataCollection.find({'tweet_id': tweet_id})
        if doc_ref.count() == 0:
            return None
        else:
            return doc_ref[0]             

    def saveTweetDetails(self, tweetDetails):
        if 'tweet_id' in tweetDetails:
            tweet_id = tweetDetails['tweet_id']
            tweetDataCollection = self.db.tweetData
            doc_ref = tweetDataCollection.find({'tweet_id': tweet_id})
            if doc_ref.count() == 0:
                print(f" tweet add {tweetDetails}")
                tweetDataCollection.insert_one(tweetDetails)
            else:
                print(f" tweet update {tweetDetails}")
                tweetDataCollection.update({'tweet_id': tweet_id}, tweetDetails)
    
    def getNotAddressedTwitterEvents(self):
        twitterEventDataCollection = self.db.twitter_events
        doc_ref = twitterEventDataCollection.find({'addressed': False})
        if doc_ref.count() == 0:
            return None
        else:
            return doc_ref[2]
        
    def saveTwitterEventDetails(self, event_id, addressed):
        twitterEventDataCollection = self.db.twitter_events
        doc_ref = twitterEventDataCollection.find({'event_id': event_id})
        if doc_ref.count() == 0:
            print(f" twitter event not found add")
        else:
            print(f" twitter event update ")
            twitterEventDataCollection.update({'event_id': event_id}, {'addressed' : addressed})