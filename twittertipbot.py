
import tweepy
from tweepy import OAuthHandler
from tweepy import API
from secretes import Secretes
from time import sleep
from datastore import DataStore
from hmyclient import HmyClient
from utility import Utility
import subprocess

class TwitterTipBot():
    auth = None
    api = None
    stream = None
    twitter_uid = "1190625904717959169"
    bot_twitter_handle = "prarysoft"
    dataStore = None
    explorer_url = 'https://explorer.pops.one/#' #'https://explorer.harmony.one/#'

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
            twitter_event_details = self.dataStore.getNotAddressedTwitterEvents()
            if twitter_event_details != None:
                try:
                    text = twitter_event_details['event_text']
                    if f'@{self.bot_twitter_handle} !tip' in text:
                        self.process_tip(twitter_event_details['event_id'], text, twitter_event_details['sender_handle'], twitter_event_details['receiver_handle'])
                    elif text == '!history':
                        self.history(twitter_event_details['sender_handle'], twitter_event_details['sender_id'])
                    elif text == '!help':
                        self.help(twitter_event_details['sender_id'])
                    elif text == '!balance':
                        self.balance(twitter_event_details['sender_handle'], twitter_event_details['sender_id'])
                    elif text.startswith("!withdraw"):
                        self.withdraw(text, twitter_event_details['sender_handle'], twitter_event_details['sender_id'])
                    elif text.startswith("!deposit"):
                        self.deposit(twitter_event_details['sender_handle'], twitter_event_details['sender_id'])
                    elif text.startswith("!verify"):
                        self.verify_twitter(text, twitter_event_details['sender_handle'], twitter_event_details['sender_id'])                                         
                except Exception as ex:
                    print(ex)
                finally:
                    if 'event_id' in twitter_event_details:
                        twitter_event_details['addressed'] = True
                        self.dataStore.saveTwitterEventDetails(twitter_event_details)
            sleep(10)

    # When someone wants to deposit one to his account
    def deposit(self, sender_handle, sender_id):
        try:
            user_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{sender_handle}')
            if user_details != None:
                one_address = user_details['one_address']
                try:
                    img = self.api.media_upload(Utility.getQRCodeImageFilePath(one_address))
                    self.api.send_direct_message(text=f'Your Deposit address is: {one_address}', recipient_id=sender_id, attachment_type='media', attachment_media_id=img.media_id)
                except Exception as e:
                    self.api.send_direct_message(text=f'Your Deposit address is: {one_address}', recipient_id=sender_id)
                    print(e)
            else:
                self.api.send_direct_message(text="You\'re not registered! Please register using the Telegram bot (https://t.me/onetipbot).", recipient_id=sender_id)
        except Exception as ex:
            print(ex)


    def withdraw(self, text, sender_handle, sender_id):
        parts = text.split(" ")
        withdraw_address = ""
        amount = 0
        inputInValid = False
        reply_message = ""
        user_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{sender_handle}')
        from_address = user_details['one_address']
        if len(parts) >= 3:
            if parts[0] == "!withdraw":
                print(text)
                try:
                    amount = float(parts[1])
                except Exception as ex:
                    inputInValid = True
                    reply_message = "Invalid withdrawal amount."
                    print(ex)
                if not inputInValid:
                    if amount < 0.00000000:
                        reply_message = f"Withdrawal amount cannot be negative."
                        print(reply_message)
                        inputInValid = True
                    else:
                        if HmyClient.getBalance(from_address) + 0.00000021 < float(amount):
                            inputInValid = True
                            reply_message = f"Please make sure you have enough funds plus the necessary fees for the transfer."
                            print(reply_message)
                if not inputInValid:                
                    withdraw_address = parts[2]
                    if not HmyClient.validateONEAdress(withdraw_address):
                        inputInValid = True        
                        reply_message = "Invalid ONE address, transfer cancelled!"
                        print(reply_message)

        if not inputInValid:
            res = HmyClient.transfer(from_address, withdraw_address, amount)
            res = eval(res)
            if 'transaction-hash' in res:
                reply_message = f"Withdrawal completed! Receipt: {self.explorer_url}/tx/{res['transaction-hash']}"
            else:
                reply_message = "Withdrawal has failed with an unknown error."
        else:
            if reply_message == "":
                reply_message = "Unknown Error!"

        print(f'Withdraw reply :{reply_message}')        
        self.api.send_direct_message(text=reply_message, recipient_id=sender_id)

    # When someone wants to deposit one to his account
    def balance(self, sender_handle, sender_id):
        try:
            # If they're not registered nor have they received any tips without an account
            user_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{sender_handle}')
            if user_details != None:
                one_address = user_details['one_address']
                balance = HmyClient.getBalance(one_address)
                self.api.send_direct_message(text=f'Your Wallet Balance is: {balance}', recipient_id=sender_id)
            else:
                self.api.send_direct_message(text=f'You\'re not registered! Please register using the Telegram bot (https://t.me/onetipbot).i If you are already registered please link you twitter handle.', recipient_id=sender_id)
            # Save the data
        except Exception as ex:
            print(ex)

    # When someone wants to see the History of his account
    def history(self, sender_handle, sender_id):
        try:
            # If they're not registered nor have they received any tips without an account
            user_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{sender_handle}')
            if user_details != None:
                one_address = user_details['one_address']
                self.api.send_direct_message(text=f'Account History: {self.explorer_url}/address/{one_address}', recipient_id=sender_id)
            else:
                self.api.send_direct_message(text=f'You\'re not registered! Please register using the Telegram bot (https://t.me/onetipbot)', recipient_id=sender_id)                
        except Exception as ex:
            print(ex)

    def help(self, sender_id):
        try:
            help_text = u"Deposit \n----------------\n\nTo get started using @OneTipBot you need to deposit funds to your address. Sent a direct message to the @onetipbot using \" !deposit\" to find out your deposit address.\n\n\nWithdraw\n----------------\n\nTo Withdraw funds from @OneTipBot you need to send \"!withdraw <amount> <one_address>\". Make sure you have enough funds to cover the amount you want to send plus the network fees.\n\n\nTip\n-----------------\n\nYou can tip anyone by replying tweets using: @OneTipBot !tip <tip_amount> <twitter_handle> \n\n\nVerify Twitter Ownership\n-----------------\n\n\nTo verify twitter ownership type !verify <telegram_handle>.\n\n\nDisclaimer\n-----------------\n\nPrivate keys are managed by @OneTipBot and securely stored. The bot uses the private key to create transactions on your behalf via telegram bot. It is not recommended to store large quantities of your crypto on @OneTipBot."
            self.api.send_direct_message(text=help_text, recipient_id=sender_id)
        except Exception as ex:
            print(ex)
        

    def process_tip(self, tweet_id, text, sender_handle, receiver):
        tip = 0
        success = "yes"
        failure_reason = ""
        tweet_type = "tweet"
        reply_text = ""
        print(text)
        print(f'@{self.bot_twitter_handle} !tip')
        if f'@{self.bot_twitter_handle} !tip' in text:
            if not self.dataStore.checkIftweetDataExists(tweet_id): 
                sender_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{sender_handle}')
                if sender_details != None:
                    if 'twitter_handle_verified' in sender_details:
                        if sender_details['twitter_handle_verified'] == True:
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
                                    from_balance = HmyClient.getBalance(from_address)
                                    if tip + 0.00000021 > from_balance:
                                        reply_text = f'@{sender_handle}, your balance is too low to tip {tip} ONE.'
                                    else:
                                        receiver_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{receiver}')
                                        if receiver_details == None:
                                            reply_text = f"@{sender_handle}, @{receiver} is not registered! Please register using Telegram the bot (https://t.me/onetipbot)."
                                        else:
                                            if 'one_address' in receiver_details:
                                                res = HmyClient.transfer(from_address, receiver_details['one_address'], tip)
                                                res = eval(res)
                                                if 'transaction-hash' in res:
                                                    reply_text = f"Hi @{receiver}, @{sender_handle} just tipped you {tip} ONE."
                                                else:
                                                    print(f"Tip failed from {sender} to {receiver} tip {tip} ONE.")
                                            else:
                                                print('Receiver address is missing!')
                                else:
                                    reply_text = f'@{sender_handle} You can\'t tip yourself!'
                            else:
                                reply_text = f'@{sender_handle} Please, mention a receiver when tipping! Check !help for more detailed instructions.'
                        else:
                            success = "no"
                            failure_reason = "twitter account not verified"
                            reply_text = f'@{sender_handle} Your twitter handle is not verified! Please verify using the Telegram bot (https://t.me/onetipbot).'                            
                    else:
                        success = "no"
                        failure_reason = "twitter account not verified"
                        reply_text = f'@{sender_handle} Your twitter handle is not verified! Please verify using the Telegram bot (https://t.me/onetipbot).'                        
                else:
                    success = "no"
                    failure_reason = "account does not exists"
                    reply_text = f'@{sender_handle} You are not registered! Please register using the Telegram bot (https://t.me/onetipbot).'
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

    def verify_twitter(self, text, sender_handle, sender_id):
        parts = text.split(" ")
        reply_message = ""
        user_details = self.dataStore.getUserDetailsByTwitterHandle(f'@{sender_handle}')
        telegram_user_id = ""
        if len(parts) == 2:
            if parts[0] == "!verify":
                telegram_user_id = parts[1]
        if user_details != None:
            if user_details['telegram_user_id'] == telegram_user_id:
                reply_message = f"Congratulations, your twitter handle is verified! Check !help for more detailed instructions on how to start tipping."
                user_details['twitter_handle_verified'] = True
                self.dataStore.saveUserDetails(user_details)
            else:
                reply_message = f"Sorry, we were not able to verify your twitter handle! Please retry using the Telegram bot (https://t.me/onetipbot)."
        else:
            reply_message = f"Sorry, were not able to verify your twitter handle! Please retry using the Telegram bot (https://t.me/onetipbot)."
        
        self.api.send_direct_message(text=reply_message, recipient_id=sender_id)
    
twitterBot = TwitterTipBot()
twitterBot.startTwitterTipBot()
