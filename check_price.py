import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time
import logging

# Set up logging
logging.basicConfig(filename='/usr/src/app/app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration from environment variables
URL = os.getenv('PRODUCT_URL', 'https://www.amazon.com/gp/product/B0D5B7GFLB/ref=ox_sc_act_title_1?smid=A1NNDL37T76WIA&psc=1')
HEADERS = {
    'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'),
    'Accept-Language': os.getenv('ACCEPT_LANGUAGE', 'en-US, en;q=0.5')
}
PRICE_FILE = os.getenv('PRICE_FILE', 'price_log.csv')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 86400))  # Default 24 hours in seconds

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_telegram_notification(title, body):
    """Send a Telegram notification."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': f'*{title}*\n{body}',
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info('Notification sent to Telegram successfully.')
    except requests.RequestException as e:
        logging.error(f'Failed to send notification to Telegram: {e}')


def get_current_price():
    """Fetch the current price of the product."""
    try:
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        product_title = soup.find('span', {'id': 'productTitle'}).text.strip()
        price = soup.find('span', {'class': 'aok-offscreen'}).text.strip()
        return product_title, price
    except requests.RequestException as e:
        logging.error(f'Error fetching the product page: {e}')
        return None, None


def write_price_to_csv(date, csv_time, product_title, price):
    """Write the product price to the CSV file."""
    file_exists = os.path.exists(PRICE_FILE)
    try:
        with open(PRICE_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                logging.info(f"Creating new CSV file: {PRICE_FILE}")
                writer.writerow(['Date', 'Time', 'Product Title', 'Price'])
            logging.info(f"Appending to CSV file: {PRICE_FILE}")
            writer.writerow([date, csv_time, product_title, price])
    except IOError as e:
        logging.error(f'Error writing to the CSV file: {e}')


def check_price_drop():
    """Check for a price drop and notify if necessary."""
    product_title, current_price = get_current_price()
    if not product_title or not current_price:
        return

    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    try:
        with open(PRICE_FILE, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            last_row = rows[-1] if rows else []
            previous_price = last_row[3] if len(last_row) > 3 else None
    except Exception as e:
        logging.error(f"Error reading the CSV file: {e}")
        previous_price = None

    if previous_price is None:
        write_price_to_csv(date_str, time_str, product_title, current_price)
    elif current_price != previous_price:
        title = 'Price Drop Alert!'
        body = f'{product_title}\nOld Price: {previous_price}\nNew Price: {current_price}'
        send_telegram_notification(title, body)
        write_price_to_csv(date_str, time_str, product_title, current_price)


def notify_start():
    """Notify when the script starts."""
    title = 'Script Started'
    body = 'The price tracking script has started successfully.'
    send_telegram_notification(title, body)


def main():
    """Main function to run the script."""
    notify_start()  # Notify when the script starts
    while True:
        check_price_drop()
        time.sleep(CHECK_INTERVAL)  # Sleep for specified interval


if __name__ == "__main__":
    main()
