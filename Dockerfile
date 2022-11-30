# Base Docker
FROM yasirarism/misskaty-docker:latest

COPY . .
# Set CMD Bot
CMD ["python3", "-m", "misskaty"]
