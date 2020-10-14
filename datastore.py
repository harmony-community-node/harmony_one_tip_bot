import pymongo
from pymongo import MongoClient

class DataStore:

    client = None
    db = None
    usersData = u'usersData'

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

    def saveUserDetails(self, userDetails):
        if 'chat_id' in userDetails and 'telegram_user_id' in userDetails:
            userDataCollection = self.db.usersData
            doc_ref = userDataCollection.find({"$and":[{'chat_id' : userDetails['chat_id']}, {'telegram_user_id': userDetails['telegram_user_id']}]})
            if doc_ref.count() == 0:
                #print(f" add {addressData}")
                userDataCollection.insert_one(userDetails)
            else:
                #print(f"update {addressData}")
                for doc in doc_ref:
                    print(doc.id)
                    userDataCollection.update({ "$and" : [{'chat_id' : userDetails['chat_id']}, {'telegram_user_id': userDetails['telegram_user_id']}]}, userDetails)

    def getUserDetails(self, chat_id, telegram_user_id):
        userDataCollection = self.db.usersData
        doc_ref = userDataCollection.find({"$and":[{'chat_id' : chat_id}, {'telegram_user_id': telegram_user_id}]})
        if doc_ref.count() == 0:
            return None
        else:
            return doc_ref[0]