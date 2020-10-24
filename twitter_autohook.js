const { Autohook } = require('twitter-autohook');
const secretes = require('./secretes');
var mongoose = require("mongoose");
var Schema = mongoose.Schema;

var twitter_events = new Schema({
  event_id: String,
  event_text: String,
  sender_handle: String,
  receiver_handle: String,
  event_type: String,
  addressed: Boolean
}, {
  collection: 'twitter_events'
});
var Model = mongoose.model('twitter_events', twitter_events);
mongoose.Promise = global.Promise; mongoose.connect("mongodb://localhost:27017/one_tip_bot_data");

const botTwitterId = "1190625904717959169";
const botHandle = "@prarysoft";

(async ƛ => {
  const webhook = new Autohook({
    token: secretes.TWITTER_ACCESS_TOKEN,
    token_secret: secretes.TWITTER_ACCESS_TOKEN_SECRET,
    consumer_key: secretes.TWITTER_CONSUMER_KEY,
    consumer_secret: secretes.TWITTER_CONSUMER_SECRET,
    env: secretes.TWITTER_WEBHOOK_ENV,
    port: 1337
  });

  // Removes existing webhooks
  await webhook.removeWebhooks();

  // Listens to incoming activity
  webhook.on('event', event => {
    //console.log('Something happened:', event)
    var event_id = '';
    var event_text = '';
    var addEvent = false;
    var sender_handle = '';
    var receiver_handle = '';
    var event_type = '';
    if (event.hasOwnProperty('tweet_create_events')) {
      if (event['tweet_create_events'].length > 0) {
        var tweet = event['tweet_create_events'][0];
        event_text = tweet['text'];
        if (event_text.startsWith(botHandle + " !tip")) {
          addEvent = true;
          event_type = 'TIP';
          event_id = tweet['id_str'];
          sender_handle = tweet['user']['screen_name'];
          for(var i = 0; i < tweet['entities']['user_mentions'].length; i++)
          {
            var user = tweet['entities']['user_mentions'][i];
            if(botHandle != "@"+user['screen_name'])
            {
              receiver_handle = user['screen_name'];
              break;
            }
          }
        }
      }
    }
    else if (event.hasOwnProperty('direct_message_events')) {
      if (event['direct_message_events'].length > 0) {
        var message = event['direct_message_events'][0];
        if (message != null) {
          event_text = message['message_create']['message_data']['text'];
          if ((event_text == "!balance") || (event_text == "!withdraw") || (event_text == "!help")) {
            addEvent = true;
            event_type = 'DM';
            event_id = message['id'];
          }
        }
      }
    }
    if (addEvent) {
      console.log('Added event');
      var savedata = new Model({
        'event_id': event_id,
        'event_text': event_text,
        'sender_handle': sender_handle,
        'receiver_handle': receiver_handle,
        'event_type': event_type,
        'addressed': false // Time of save the data in unix timestamp format
      }).save(function (err, result) {
        if (result) {
          //console.log(result);
        }
      });
    }
    else {
      console.log('Event Not Added:', event);
    }
  });

  // Starts a server and adds a new webhook
  await webhook.start();

  // Subscribes to a user's activity
  const oauth_token = secretes.TWITTER_ACCESS_TOKEN;
  const oauth_token_secret = secretes.TWITTER_ACCESS_TOKEN_SECRET;
  await webhook.subscribe({ oauth_token, oauth_token_secret });
})();