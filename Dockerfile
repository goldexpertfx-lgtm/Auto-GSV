FROM python:3.11-slim

# System path set karne ke liye
WORKDIR /app

# Dependencies install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pura code copy karein (dot ke baad space ka dhyan rakhein)
COPY . .

# Environment variable check karne ke liye
ENV PYTHONUNBUFFERED=1

# Bot ko run karne ki command
CMD ["python", "bot.py"]
