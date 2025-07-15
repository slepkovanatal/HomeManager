# Use official Python base image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot code
COPY . .

# Set environment variables (optional, e.g., for time zone)
# ENV TZ=Europe/Istanbul

# Run your bot
CMD ["python", "-u", "main.py"]