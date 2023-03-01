## Bot Configuration

### BotFather

To create a Telegram bot, you have to configure it through messaging [BothFather](https://telegram.me/BotFather) and follow the options after sending the `/start` command (i.e., `/newbot`, choose the name of the bot, ...). You can find more information in [the docs](https://core.telegram.org/bots/features#botfather).

You will be given the bot token you need to use in your `.yaml`. You will use this token and the `chat_id` of the Telegram user you want to send messages to.

### RawDataBot

To get your `chat_id`, contact @RawDataBot and you will be given an output with a field `id` within `chat`.

## Saving credentials

Save a `.yaml` file with your credentials. As an example, we provide `fw_bot_example.yaml`

```
[telegram]
bot_name = YOUR_BOT_NAME_HERE
bot_token = YOUR_BOT_TOKEN_HERE
chat_id = YOUR_CHAT_ID_HERE
```

## Testing!

Test your bot before launching your experiments. This is the function that sends messages

```
import requests

bot_token = YOUR_BOT_TOKEN_HERE
chat_id = YOUR_CHAT_ID_HERE

def send_tg_message (message):
    # Telegram send message URL
    sendURL = 'https://api.telegram.org/bot' + bot_token + '/sendMessage'
    response = requests.post(sendURL + "?chat_id=" + str(chat_id) + "&text=" + message)
    # Close to avoid filling up the RAM.
    response.close()

send_tg_message(message = "Testing Bot")
```

If the test works, it's likely that you will be able to receive messages from FEDWatcher when you start the experiment (you will be asked to select the `.yaml` with your credentials).

You will receive confirmation messages for the start of experiments. For example:

```
FEDWatcher Started 2023-02-16T16:34:07.158244
Notification frequency set to 6 hours
```