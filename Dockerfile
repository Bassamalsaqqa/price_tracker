# Dockerfile
FROM python:3.9-slim

WORKDIR /usr/src/app

COPY check_price.py .
COPY Docker_bot_details.env .

RUN pip install --no-cache-dir requests beautifulsoup4

# Use a volume to map the current directory for debugging
VOLUME ["/usr/src/app"]

CMD ["python", "./check_price.py"]