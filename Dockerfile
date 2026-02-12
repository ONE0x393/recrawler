# Python 3.11 slim image
FROM python:3.11-slim

# Set timezone to Asia/Seoul
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory
WORKDIR /app

# Install system dependencies (if any needed for extensions, usually none for basic bots)
# RUN apt-get update && apt-get install -y --no-install-recommends ...

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for data volume
RUN mkdir -p /data

# Define volume for persistence
VOLUME ["/data"]

# Run the bot
CMD ["python", "run.py"]
