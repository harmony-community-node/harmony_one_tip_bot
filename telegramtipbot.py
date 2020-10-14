from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, PicklePersistence
import time, sys, signal
import logging
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
    FIRST, SECOND = range(2)

    def __init__(self):

        self.dataStore = DataStore()

        self.pp = PicklePersistence(filename='tipbot')

        self.upd = Updater(Secretes._telegram_bot_key, persistence = self.pp, use_context=True)
        self.dp = self.upd.dispatcher

        # Restores memory to the bot
        self.pp.get_chat_data()
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_handler(CallbackQueryHandler(self.register, pattern='^register$', pass_user_data=True, pass_chat_data=True))
        self.dp.add_handler(CallbackQueryHandler(self.help, pattern='^help$', pass_user_data=True, pass_chat_data=True))
        self.dp.add_handler(CallbackQueryHandler(self.balance, pattern='^balance$', pass_user_data=True, pass_chat_data=True))
        self.dp.add_handler(CallbackQueryHandler(self.history, pattern='^history$', pass_user_data=True, pass_chat_data=True))
        self.dp.add_handler(CallbackQueryHandler(self.deposite, pattern='^deposite$', pass_user_data=True, pass_chat_data=True))
        self.dp.add_handler(CommandHandler('tip', self.tip))
        

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
    def deposite(self, update, context):
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
                history = HmyClient.getTransactionHistory(one_address)
                context.bot.send_message(text=f'Your Wallet Balace \n{history}', chat_id=self.message.chat.id)
            else:
                context.bot.send_message(text='You\'re not registered!, please register to get ONE balance', chat_id=self.message.chat.id)
            # Save the data
            self.pp.update_chat_data(self.message.chat.id, context.chat_data)
        except Exception as ex:
            print(ex)
            logging.error(ex)
        finally:
            self.send_menu(update, context)            

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
                [InlineKeyboardButton("\U00002b07 Deposite", callback_data="deposite"),
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
        self.send_menu(update, context)

    def tip(self, update, context, *args):
        try:
            reply = update.message.reply_to_message
            sender = update.message.from_user.id
            # If the sender isn't in the database, there's no way they have money
            if sender in context.chat_data:
                # We only let registered users spend money, regardless of the ownership
                if context.chat_data[sender]['registered']:
                    reply = update.message.reply_to_message
                    # These IDs will be used to look up the two people in the database
                    sender = update.message.from_user.id
                    receiver = reply.from_user.id
                    # Can't tip yourself
                    if sender != receiver:
                        # The *args dict only stores strings, so we make it a number
                        tip = float(context.args[0])				
                        # Can't tip more than you have
                        if tip > context.chat_data[sender]['balance']:
                            update.message.reply_text('Sorry, your balance is too low!')
                        else:
                            # Tip is transferred
                            context.chat_data[sender]['balance'] -= tip
                            try:
                                context.chat_data[receiver]['balance'] += tip
                                update.message.reply_text('You have tipped {} {} magic beans!\nYour balance is now {} magic beans\
                                    '.format(context.chat_data[receiver]['name'], tip, context.chat_data[sender]['balance']))
                            # This means the user doesn't have registered or unregistered balance
                            except KeyError:
                                # We make them an unregistered bank account that will store beans, but won't let them spend any
                                context.chat_data.update({receiver: {'balance': tip, 'name': reply.from_user.full_name, 'registered': False}})
                                update.message.reply_text('Seems like {} doesn\'t have an account with us yet! Your tip will be waiting for them with us\n\
                                    Your balance is now {} magic beans'.format(context.chat_data[receiver]['name'], context.chat_data[sender]['balance']))		
                    else:
                        update.message.reply_text('You can\'t tip yourself!')
                # Unregistered users get this
                else:
                    update.message.reply_text('Alas, even though you might have the beans, we can\'t manage them if you\'re not a client... /register an account with us, perhaps?')
            else:
                update.message.reply_text('You don\'t expect us to tip someone with non-existent beans, do you?\nI heard you get a 200 bean bonus if you /register a bank account with us ;)')
        # This means the message doesn't contain a reply, which is required for the command
        except AttributeError:
            update.message.reply_text('You must be replying to a message to tip someone!')
        self.pp.update_chat_data(update.message.chat.id, context.chat_data)

