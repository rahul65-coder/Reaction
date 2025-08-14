import asyncio
import random
import aiohttp
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

#  ^|^e Your 5 bot tokens
BOT_TOKENS = [
    "8458550542:AAFXEaZ_PbgR6D3zi3eBWoZPME4YAJ6FWPY",  # Old bot
    "8057181584:AAEKvtV85uZwUmY3BX0gHlOJsr9uC7nU410",
    "7681907786:AAE67X6xIZHobYcKrkkk7zvF45peaRyOAnk",
    "7954292419:AAH7XtlSRtNIFMVQoS6PJ9ST2QqSC17x_j4",
    "8270199619:AAHLimPDAdstKvUjXfv8XbkCDF6bYJBMPpg"
]

#  ^|^e Only Telegram-allowed emojis (your list)
EMOJI_LIST = [
    " ^}   ^o", " ^=^q^m", " ^=^t ", " ^=^x^m", " ^=  ", " ^=^q^o", " ^=^x^a", " ^=^x ", " ^=^x ", " ^=^n^i",
    " ^= ^t", " ^=^x^f", " ^=^r ", " ^=^x^b", " ^z ", " ^=  ", " ^=^r^t", " ^=^m^s", " ^=^x^n", " ^=^q^n",
    " ^=^x^x", " ^=^x^h", " ^=  ", " ^=^x^g"
]

#  ^=^r  Direct API reaction
async def send_reaction(bot_token, chat_id, message_id, emoji):
    api_url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload) as resp:
            if resp.status == 200:
                print(f" ^|^e Bot reacted with {emoji}")
            else:
                print(f" ^}^l Reaction failed (resp.status}) for bot")

#  ^=^s  Handle incoming message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message:
        chat_id = message.chat_id
        msg_id = message.message_id
        print(f" ^=^s  Message: ID {msg_id} from chat {chat_id}")

        emojis = random.sample(EMOJI_LIST, k=len(BOT_TOKENS))
        tasks = []
        for i, token in enumerate(BOT_TOKENS):
            emoji = emojis[i % len(emojis)]
            tasks.append(send_reaction(token, chat_id, msg_id, emoji))
        await asyncio.gather(*tasks)

#  ^=^z^` Start bot
async def main():
    print(" ^= ^v 5x Bot Reactions Activated!")
    app = ApplicationBuilder().token(BOT_TOKENS[0]).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

#  ^= ^d UserLAnd / Jupyter support
nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
