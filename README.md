Price Tracker

A Dockerized script for tracking price changes of a product on Amazon and sending notifications via Telegram.

Table of Contents

•	Overview

•	Features

•	Requirements

•	Setup

•	Configuration

•	Usage

•	Health Check

•	Updating the Image

•	License

Overview

This project is a Dockerized application that tracks the price of a specified product on Amazon and sends notifications to a Telegram chat when a price change is detected. The application uses a Python script that periodically checks the price and logs it to a CSV file.

Features

•	Track price changes for a specific Amazon product.

•	Log price changes to a CSV file.

•	Send notifications to a Telegram chat on price changes.

•	Configurable via environment variables and Docker secrets.

Requirements

•	Docker

•	Docker Compose (for easier management of multi-container Docker applications)

Setup

1.	Clone the Repository

git clone https://github.com/your-username/price_tracker.git

cd price_tracker

2.	Create Docker Secrets

You need to create Docker secrets for the Telegram bot token and chat ID:

echo "your-telegram-bot-token" | docker secret create telegram_bot_token -

echo "your-telegram-chat-id" | docker secret create telegram_chat_id -

3.	Configure Environment Variables

Set the required environment variables before deploying the stack. You can do this by creating a .env file in the project directory:

PRODUCT_URL=https://www.amazon.com/gp/product/B0D5B7GFLB/ref=ox_sc_act_title_1?smid=A1NNDL37T76WIA&psc=1

USER_AGENT=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36

ACCEPT_LANGUAGE=en-US, en;q=0.5

CHECK_INTERVAL=86400

Make sure to replace the PRODUCT_URL, USER_AGENT, ACCEPT_LANGUAGE, and CHECK_INTERVAL with your desired values.

4.	Deploy the Stack

Use Docker Compose to deploy the stack:

docker stack deploy -c compose.yaml price_check

Configuration

Docker Compose Configuration


The compose.yaml file configures the Docker service and network settings:

version: '3.8'

services:

  price_tracker:
  
    image: bassamalsaqqa/price_tracker:v1.0
    
    restart: "no"
    
    secrets:
    
      - telegram_bot_token
      
      - telegram_chat_id
      
    networks:
    
      - price_tracker_network
      
    deploy:
    
      replicas: 1
      
      resources:
      
        limits:
        
          cpus: '0.5'
          
          memory: 512M
          
      update_config:
      
        parallelism: 1
        
        delay: 10s
 
      rollback_config:
      
        parallelism: 1
        
        delay: 10s

    environment:
    
      - PRODUCT_URL=${PRODUCT_URL}
      
      - USER_AGENT=${USER_AGENT}
      
      - ACCEPT_LANGUAGE=${ACCEPT_LANGUAGE}
      
      - PRICE_FILE=/usr/src/app/price_log.csv
      
      - CHECK_INTERVAL=${CHECK_INTERVAL}
    
    volumes:
    
      - data:/usr/src/app
    
    healthcheck:
    
      test: ["CMD-SHELL", "test -f /usr/src/app/price_log.csv || exit 1"]
      
      interval: 30s
      
      retries: 3
      
      start_period: 10s
      
      timeout: 10s



secrets:

  telegram_bot_token:
  
    external: true
  
  telegram_chat_id:
  
    external: true


networks:

  price_tracker_network:
  
    driver: overlay


volumes:

  data:
  
    driver: local
    
    driver_opts:
    
      o: bind
      
      device: /volume1/docker/price_check/data
      
      type: none

Environment Variables

•	PRODUCT_URL: The URL of the Amazon product to track.

•	USER_AGENT: User-Agent string to mimic a browser.

•	ACCEPT_LANGUAGE: Language preferences for the request.

•	CHECK_INTERVAL: Time interval (in seconds) between price checks.

Usage

•	Start the Application: The application is started automatically when you deploy the Docker stack.

•	Check Logs: You can view the logs of the service to monitor its activity:

docker service logs price_check_price_tracker

•	Check Service Status: To see the status of the service:

docker service ps price_check_price_tracker

Health Check

The Docker health check will verify if the CSV file price_log.csv exists. This ensures that the application is running correctly.

Updating the Image

To update the Docker image:

1.	Build the New Image: Make sure your local Docker image is updated.

2.	Push the New Image:

docker push bassamalsaqqa/price_tracker:v1.0

3.	Redeploy the Stack:

docker stack deploy -c compose.yaml price_check

License

This project is licensed under the MIT License. See the LICENSE file for details.

