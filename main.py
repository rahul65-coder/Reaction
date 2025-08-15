import asyncio
import random
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from aiohttp import web

# 5 Bots ke Tokens (ENV se secure karo!)
BOT_TOKENS = [
    "8458550542:AAFXEaZ_PbgR6D3zi3eBWoZPME4YAJ6FWPY",  # Bot 1
    "8057181584:AAEKvtV85uZwUmY3BX0gHlOJsr9uC7nU410",  # Bot 2
    "7681907786:AAE67X6xIZHobYcKrkkk7zvF45peaRyOAnk",  # Bot 3
    "7954292419:AAH7XtlSRtNIFMVQoS6PJ9ST2QqSC17x_j4",  # Bot 4
    "8270199619:AAHLimPDAdstKvUjXfv8XbkCDF6bYJBMPpg"   # Bot 5
]

# Emoji List (Telegram allowed)
EMOJI_LIST = ["❤️", "👍", "🔥", "😍", "🥰", "👏", "💋", "🏆", "🤑"]

# ✅ Reaction Bhejo (5 Bots Parallel)
async def send_reaction(bot_token, chat_id, message_id, emoji):
    api_url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"  # Fixed URL
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload) as resp:
            if resp.status == 200:
                print(f"✅ {bot_token[:5]}...: {emoji}")
            else:
                print(f"❌ {bot_token[:5]}... failed ({resp.status})")

# Message Aane Pe 5 Bots se React Kare
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message:
        chat_id = message.chat_id
        msg_id = message.message_id
        print(f"📨 Message ID: {msg_id} | Chat: {chat_id}")

        # 5 Random Emojis (1 per bot)
        emojis = random.sample(EMOJI_LIST, k=len(BOT_TOKENS))  # Fixed typo (BOT_TOKENS)
        tasks = []
        for i, token in enumerate(BOT_TOKENS):  # Fixed typo (BOT_TOKENS)
            tasks.append(send_reaction(token, chat_id, msg_id, emojis[i]))
        await asyncio.gather(*tasks)  # Parallel execution

# Render Ke Liye Health Check
async def health_check(request):
    return web.Response(text="5 Bots Chal Rahe Hai! ✅")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("🌐 Server: 8080 (Render Ke Liye)")

async def main():
    print("🚀 5 Bots Activated!")
    await start_web_server()  # Render compatibility
    
    # Bot 1 (Polling) - Baaki 4 API se react karenge
    app = ApplicationBuilder().token(BOT_TOKENS[0]).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("🤖 1 Bot Polling, 4 Bots API Mode Mein!")
    await asyncio.Event().wait()  # 24/7 Run

if __name__ == "__main__":
    asyncio.run(main())
