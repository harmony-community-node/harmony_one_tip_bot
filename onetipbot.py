from telegramtipbot import OneTipTelegramBot
from twittertipbot   import TwitterTipBot
import threading

def startTelegramBot():
   oneTipTelegramBot = OneTipTelegramBot()

def startTwitterBot():
   twitterBot = TwitterTipBot()
   twitterBot.startTwitterTipBot()

def main():
   try:
      t1 = threading.Thread(target=startTwitterBot, args=())
      t1.start()
      startTelegramBot()
   except:
      print("Error: unable to start thread")

if __name__ == '__main__':
    main()