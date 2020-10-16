from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, PicklePersistence, MessageHandler, Filters
import time, sys, signal
import logging
import json
from secretes import Secretes
from datastore import DataStore
from hmyclient import HmyClient
from utility import Utility 



# Can be anything you want
starting_bonus = 200

# The always available context dict and the ability to preserve it make for a very rudimentary database

class OneTipTelegramBot:

    pp = None
    upd = None
    dp = None
    message = None
    dataStore = None
    markup = None
    FIRST, SECOND = range(2)
    GET_ADDRESS, GET_AMOUNT, CONFIRM_TRANSFER, CANCEL_TRANSFER = range(4)
    explorer_url = 'https://explorer.pops.one/#' #'https://explorer.harmony.one/#'
    reply_keyboard = [
        ['\U0001f916 Menu'],
    ]
    transfer_date = {}

    def __init__(self):

        self.dataStore = DataStore()

        self.pp = PicklePersistence(filename='tipbot')

        self.upd = Updater(Secretes._telegram_bot_key, persistence = self.pp, use_context=True)
        self.dp = self.upd.dispatcher

        self.markup = ReplyKeyboardMarkup(self.reply_keyboard, resize_keyboard=True)
        # Restores memory to the bot
        self.pp.get_chat_data()
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_handler(MessageHandler(Filters.regex('^\U0001f916 Menu$'), self.start))
        self.dp.add_handler(CallbackQueryHandler(self.register, pattern='^register$', pass_user_data=True, pass_chat_data=True))
        self.dp.add_handler(CallbackQueryHandler(self.help, pattern='^help$'))
        self.dp.add_handler(CallbackQueryHandler(self.balance, pattern='^balance$'))
        self.dp.add_handler(CallbackQueryHandler(self.history, pattern='^history$'))
        self.dp.add_handler(CallbackQueryHandler(self.deposit, pattern='^deposit$'))
        self.dp.add_handler(CommandHandler('tip', self.tip))

        
        conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(self.withdraw, pattern='^withdraw$')],
        states={
            self.GET_ADDRESS: [
                MessageHandler(Filters.text, self.get_address),
            ],
            self.GET_AMOUNT: [
                MessageHandler(Filters.text, self.get_amount)
            ],
            self.CONFIRM_TRANSFER: [
                MessageHandler(Filters.text, self.confirm_transfer)
            ],
            self.CANCEL_TRANSFER: [
                MessageHandler(Filters.text, self.cacel_transfer)
            ],
        },
            fallbacks=[MessageHandler(Filters.regex('^start$'), self.send_menu)],
        )
        self.dp.add_handler(conv_handler)
        

        

        # Start the Bot
        self.upd.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT
        self.upd.idle()

        # Save all the data one last time when we close it with Ctrl+C in console
        self.pp.flush()

    # When someone wants to register an account
    def register(self, update, context):
        try:
            sender = self.message.from_user
            # If they're not registered nor have they received any tips without an account
            if not self.dataStore.checkIfUserRecordExists(sender.id, sender.username):
                new_one_address = HmyClient.regiterNewUser(sender.username)
                parts = new_one_address.split('\n')
                if len(parts) > 3:
                    if parts[3].startswith('ONE Address:'):
                        one_address = parts[3].replace('ONE Address: ', '')
                        user_data = {
                            'balance': 0,
                            'chat_id' : sender.id,
                            'telegram_user_id' : sender.username, 
                            'name': sender.full_name, 
                            'seed' : parts[2],
                            'one_address' : one_address
                        }
                        self.dataStore.saveUserDetails(user_data)
                        context.bot.send_message(text=f'Welcome aboard {sender.full_name}, you are successfully registered!', chat_id=self.message.chat.id)
                        context.bot.send_message(text=f'Your Deposite address {one_address}', chat_id=self.message.chat.id)
                        context.bot.send_photo(caption="Your Deposite address", chat_id=self.message.chat.id, photo=open(Utility.getQRCodeImageFilePath(one_address), 'rb'))
                    else:
                        context.bot.send_message(text='Registration failed! due to error in wallet generation', chat_id=self.message.chat.id)
                else:
                    context.bot.send_message(text='Registration failed!', chat_id=self.message.chat.id)
            else:
                context.bot.send_message(text='You\'re already registered!', chat_id=self.message.chat.id)
            # Save the data
            self.pp.update_chat_data(self.message.chat.id, context.chat_data)
        except Exception as ex:
            print(ex)
            logging.error(ex)
        finally:
            self.send_menu(update, context)

    # When someone wants to deposite one to his account
    def deposit(self, update, context):
        try:
            sender = self.message.from_user
            # If they're not registered nor have they received any tips without an account
            user_details = self.dataStore.getUserDetails(sender.id, sender.username)
            if user_details != None:
                one_address = user_details['one_address']
                context.bot.send_message(text=f'Your Deposite address {one_address}', chat_id=self.message.chat.id)
                context.bot.send_photo(caption="Your Deposite address", chat_id=self.message.chat.id, photo=open(Utility.getQRCodeImageFilePath(one_address), 'rb'))
            else:
                context.bot.send_message(text='You\'re not registered!, please register to deposite ONE', chat_id=self.message.chat.id)
            # Save the data
            self.pp.update_chat_data(self.message.chat.id, context.chat_data)
        except Exception as ex:
            print(ex)
            logging.error(ex)
        finally:
            self.send_menu(update, context)

    # When someone wants to deposite one to his account
    def balance(self, update, context):
        try:
            sender = self.message.from_user
            # If they're not registered nor have they received any tips without an account
            user_details = self.dataStore.getUserDetails(sender.id, sender.username)
            if user_details != None:
                one_address = user_details['one_address']
                balance = HmyClient.getBalace(one_address)
                context.bot.send_message(text=f'Your Wallet Balace \n{balance}', chat_id=self.message.chat.id)
            else:
                context.bot.send_message(text='You\'re not registered!, please register to get ONE balance', chat_id=self.message.chat.id)
            # Save the data
            self.pp.update_chat_data(self.message.chat.id, context.chat_data)
        except Exception as ex:
            print(ex)
            logging.error(ex)
        finally:
            self.send_menu(update, context)

    # When someone wants to see the History of his account
    def history(self, update, context):
        try:
            sender = self.message.from_user
            # If they're not registered nor have they received any tips without an account
            user_details = self.dataStore.getUserDetails(sender.id, sender.username)
            if user_details != None:
                one_address = user_details['one_address']
                context.bot.send_message(text=f'Account History\n{self.explorer_url}/address/{one_address}', chat_id=self.message.chat.id)
            else:
                context.bot.send_message(text='You\'re not registered!, please register to get Account History', chat_id=self.message.chat.id)
            # Save the data
            self.pp.update_chat_data(self.message.chat.id, context.chat_data)
        except Exception as ex:
            print(ex)
            logging.error(ex)
        finally:
            self.send_menu(update, context)

    # When someone wants to withdraw amount
    def withdraw(self, update, context):
        try:
            sender = self.message.from_user
            # If they're not registered nor have they received any tips without an account
            user_details = self.dataStore.getUserDetails(sender.id, sender.username)
            if user_details != None:
                context.bot.send_message(text=f'Please type the receiver address', chat_id=self.message.chat.id)
            else:
                context.bot.send_message(text='You\'re not registered!, please register to Deposit or Withdraw History', chat_id=self.message.chat.id)
            # Save the data
            self.pp.update_chat_data(self.message.chat.id, context.chat_data)
        except Exception as ex:
            print(ex)
            logging.error(ex)
        return self.GET_ADDRESS   

    def send_menu(self, update, context):
        #print(context.chat_data)
        #print(self.message)
        keyboard = []
        sender = self.message.from_user
        if not self.dataStore.checkIfUserRecordExists(sender.id, sender.username):
            keyboard = [
                [InlineKeyboardButton(u"\U0001f4b3 Register", callback_data="register"),
                InlineKeyboardButton(u"\U00002753 Help", callback_data="help")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("\U0001f4b0 Balance", callback_data="balance"),
                InlineKeyboardButton("\U0001f9fe History", callback_data="history")],
                [InlineKeyboardButton("\U00002b07 Deposit", callback_data="deposit"),
                InlineKeyboardButton("\U00002b06 Withdraw", callback_data="withdraw")],
                [InlineKeyboardButton(u"\U00002753 Help", callback_data="help")],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text="Please select an option:", chat_id=self.message.chat.id, reply_markup=reply_markup)

    def help(self, update, context):
        context.bot.send_message(text='Help will be printed here', chat_id=self.message.chat.id)
        self.send_menu(update, context)

    def start(self, update, context):
        self.message = update.message
        self.pp.update_chat_data(self.message.chat.id, context.chat_data)
        context.bot.send_message(chat_id = self.message.chat.id, text = "Welcome to Harmony ONE tipping bot", reply_markup = self.markup)
        self.send_menu(update, context)

    def get_address(self, update, context):
        user_data = context.user_data
        text = update.message.text


        if HmyClient.validateONEAdress(text) :
            user_data['to_address'] = text
            update.message.reply_text(f"Please enter how much you want to send it to {text}")
            return self.GET_AMOUNT
        else:
            update.message.reply_text("Invalid ONE address, transfer cancelled")
            return self.CANCEL_TRANSFER

    def get_amount(self, update, context):
        user_data = context.user_data
        text = update.message.text

        if Utility.is_valid_amount(text):
            sender = self.message.from_user
            user_details = self.dataStore.getUserDetails(sender.id, sender.username)
            if user_details != None:
                one_address = user_details['one_address']
                if HmyClient.getBalace(one_address) + 0.00000021 >= float(text):
                    user_data['amount'] = text
                    user_data['from_address'] = one_address
                    update.message.reply_text(f"Transferting {user_data['to_address']} ONE to {text}, Please type Yes/Y to confirm, any other input will cancel the transfer.")
                    return self.CONFIRM_TRANSFER
                else:
                    update.message.reply_text(f"Your current balance is lower than {text}, transfer cancelled")
                    return ConversationHandler.END
        else:
            update.message.reply_text("Invalid ONE address, transfer cancelled")
            self.send_menu(update, context)
            return ConversationHandler.END

    def confirm_transfer(self, update, context):
        user_data = context.user_data
        text = update.message.text

        if text == "Yes" or text == "Y":
            res = HmyClient.transfer(user_data['from_address'], user_data['to_address'], user_data['amount'])
            res = eval(res)
            if 'transaction-hash' in res:
                update.message.reply_text(f"Withdraw is complete, here is the receipt {self.explorer_url}/tx/{res['transaction-hash']}")
            else:
                update.message.reply_text("Withdraw is failed with unknown error")
        else:
            update.message.reply_text("Withdraw is failed")

        user_data.clear()
        self.send_menu(update, context)
        return ConversationHandler.END            

    def cacel_transfer(self, update, context):
        user_data = context.user_data
        update.message.reply_text("Cancelled the transaction")
        user_data.clear()
        self.send_menu(update, context)
        return ConversationHandler.END

    def tip(self, update, context, *args):
        try:
            reply = update.message.reply_to_message
            sender_details = self.dataStore.getUserDetails(update.message.from_user.id, update.message.from_user.username)
            if sender_details != None:
                from_address = sender_details['one_address']
                # If the sender isn't in the database, there's no way they have money
                reply = update.message.reply_to_message
                # These IDs will be used to look up the two people in the database
                sender = update.message.from_user.id
                receiver = reply.from_user.id
                # Can't tip yourself
                if sender != receiver:
                    # The *args dict only stores strings, so we make it a number
                    tip = float(context.args[0])				
                    # Can't tip more than you have
                    from_balance = HmyClient.getBalace(from_address)
                    if tip + 0.00000021 > from_balance:
                        update.message.reply_text(f'Sorry, your balance is low! tip {tip}')
                    else:
                        receiver_details = self.dataStore.getUserDetails(reply.from_user.id, reply.from_user.username)
                        if receiver_details == None:
                            # Unregistered users get this and they will be registered automatically
                            new_one_address = HmyClient.regiterNewUser(sender.username)
                            parts = new_one_address.split('\n')
                            if len(parts) > 3:
                                if parts[3].startswith('ONE Address:'):
                                    to_address = parts[3].replace('ONE Address: ', '')
                                    receiver_details = {
                                        'balance': 0,
                                        'chat_id' : reply.from_user.id,
                                        'telegram_user_id' : reply.from_user.username, 
                                        'name': reply.from_user.full_name, 
                                        'seed' : parts[2],
                                        'one_address' : to_address
                                    }
                                    self.dataStore.saveUserDetails(receiver_details)
                        if 'one_address' in receiver_details:
                            res = HmyClient.transfer(from_address, receiver_details['one_address'], tip)
                            res = eval(res)
                            if 'transaction-hash' in res:
                                update.message.reply_text(f"Hi {reply.from_user.username}, {update.message.from_user.username} just tipped you {tip} ONE")
                            else:
                                print(f"Tip failed from  {update.message.from_user.username} to {reply.from_user.username} tip {tip} ONE")
                else:
                    update.message.reply_text('You can\'t tip yourself!')
        # This means the message doesn't contain a reply, which is required for the command
        except AttributeError as ae:
            print(ae)
            update.message.reply_text('You must be replying to a message to tip someone!')
        self.pp.update_chat_data(update.message.chat.id, context.chat_data)

