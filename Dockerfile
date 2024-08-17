# Dockerfile
FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY check_price.py .
COPY Docker_bot_details.env .

# Create logs directory
RUN mkdir -p /usr/src/app/logs

VOLUME ["/usr/src/app/logs"]

CMD ["python", "./check_price.py"]
