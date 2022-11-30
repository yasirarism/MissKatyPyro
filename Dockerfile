# Base Docker
FROM misskaty-docker:latest

COPY . .
# Set CMD Bot
CMD ["python3", "-m", "bot"]
