import asyncio
import random
import aiohttp
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from aiohttp import web
from collections import defaultdict

# Configuration
BOT_TOKENS = [
    "8458550542:AAFXEaZ_PbgR6D3zi3eBWoZPME4YAJ6FWPY",  # Old bot
    "8057181584:AAEKvtV85uZwUmY3BX0gHlOJsr9uC7nU410",
    "7681907786:AAE67X6xIZHobYcKrkkk7zvF45peaRyOAnk",
    "7954292419:AAH7XtlSRtNIFMVQoS6PJ9ST2QqSC17x_j4",
    "8270199619:AAHLimPDAdstKvUjXfv8XbkCDF6bYJBMPpg"
]

EMOJI_LIST = [
    "❤️", "👍", "🔥", "😍", "🥰", "👏", "💋", "🏆", "🤑",
    "🎉", "💸", "☠️", "💯", "", "⚡", "🤩", "",
    "☠", "😎", "", "😘", "😈", "🤯", "😇"
]

# Rate limiting and concurrency control
MESSAGE_LOCK = asyncio.Lock()
ACTIVE_TASKS = defaultdict(set)
MAX_CONCURRENT_MESSAGES = 10  # Adjust based on your needs

async def send_reaction(bot_token, chat_id, message_id, emoji):
    api_url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}]
    }
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(api_url, json=payload) as resp:
                if resp.status == 200:
                    print(f"✅ Reaction success with {emoji} (Bot: {bot_token[-4:]})")
                else:
                    error = await resp.text()
                    print(f"❌ Reaction failed ({resp.status}) for bot {bot_token[-4:]}: {error}")
    except Exception as e:
        print(f"⚠️ Network error for bot {bot_token[-4:]}: {str(e)}")

async def process_message(chat_id, message_id):
    emojis = random.sample(EMOJI_LIST, k=len(BOT_TOKENS))
    tasks = []
    
    for i, token in enumerate(BOT_TOKENS):
        emoji = emojis[i % len(emojis)]
        tasks.append(send_reaction(token, chat_id, message_id, emoji))
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Clean up
    async with MESSAGE_LOCK:
        ACTIVE_TASKS[chat_id].discard(message_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    chat_id = message.chat_id
    msg_id = message.message_id
    
    async with MESSAGE_LOCK:
        # Check if we're already processing this message
        if msg_id in ACTIVE_TASKS[chat_id]:
            print(f"⏩ Already processing message {msg_id} in chat {chat_id}")
            return
        
        # Check concurrency limits
        if len(ACTIVE_TASKS[chat_id]) >= MAX_CONCURRENT_MESSAGES:
            print(f"🚫 Too many concurrent messages for chat {chat_id} (max {MAX_CONCURRENT_MESSAGES})")
            return
            
        ACTIVE_TASKS[chat_id].add(msg_id)
    
    print(f"📨 Message received — ID: {msg_id} | Chat: {chat_id}")
    asyncio.create_task(process_message(chat_id, msg_id))

async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web server started on port 8080")

async def cleanup_tasks():
    """Periodically clean up completed tasks"""
    while True:
        await asyncio.sleep(3600)  # Cleanup every hour
        async with MESSAGE_LOCK:
            for chat_id in list(ACTIVE_TASKS.keys()):
                if not ACTIVE_TASKS[chat_id]:
                    del ACTIVE_TASKS[chat_id]

async def main():
    print("🚀 Enhanced 5x Bot Reactions Activated!")
    
    # Start web server
    await start_web_server()
    
    # Start cleanup task
    asyncio.create_task(cleanup_tasks())
    
    # Start Telegram bot
    app = ApplicationBuilder().token(BOT_TOKENS[0]).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep running
    await asyncio.Event().wait()

# UserLAnd / Jupyter support
nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
