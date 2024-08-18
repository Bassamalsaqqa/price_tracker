import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time
import logging
import docker
from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set up logging
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'app.log')

logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration from environment variables
URL = os.getenv('PRODUCT_URL', 'https://www.amazon.com/gp/product/B0D5B7GFLB/ref=ox_sc_act_title_1?smid=A1NNDL37T76WIA&psc=1')
HEADERS = {
    'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'),
    'Accept-Language': os.getenv('ACCEPT_LANGUAGE', 'en-US, en;q=0.5')
}
PRICE_FILE = os.getenv('PRICE_FILE', 'logs/price_log.csv')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 86400))  # Default 24 hours in seconds

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = Bot(token=TELEGRAM_BOT_TOKEN)
client = docker.from_env()

# Define command handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Bot is running. Use /help to see available commands.')

def help_command(update: Update, context: CallbackContext):
    commands = [
        '/status - Check container health status',
        '/logs - Get the latest logs',
        '/price - Get the current product price',
        '/running - Check if the container is running',
        '/help - List available commands',
    ]
    update.message.reply_text("\n".join(commands))

def status(update: Update, context: CallbackContext):
    container = client.containers.get('amazon_price_tracker-price_tracker-1')
    health_status = container.attrs['State']['Health']['Status']
    update.message.reply_text(f'Container health status: {health_status}')

def logs(update: Update, context: CallbackContext):
    with open(log_file_path, 'r') as log_file:
        logs = log_file.read()[-4096:]  # Last 4096 characters of logs
    update.message.reply_text(f"Logs:\n```\n{logs}\n```", parse_mode=ParseMode.MARKDOWN)

def price(update: Update, context: CallbackContext):
    product_title, current_price = get_current_price()
    if product_title and current_price:
        update.message.reply_text(f'Current price of {product_title}: {current_price}')
    else:
        update.message.reply_text('Failed to retrieve the current price.')

def running(update: Update, context: CallbackContext):
    container = client.containers.get('amazon_price_tracker-price_tracker-1')
    status = container.status
    update.message.reply_text(f'Container running status: {status}')

# Set up the bot with the command handlers
def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CommandHandler('logs', logs))
    dispatcher.add_handler(CommandHandler('price', price))
    dispatcher.add_handler(CommandHandler('running', running))
    
    notify_start()
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
