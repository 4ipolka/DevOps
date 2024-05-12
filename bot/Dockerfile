FROM python:3.9-slim
WORKDIR /bot
COPY bot/. .
RUN apt update && apt-get install libpq-dev build-essential python3-dev -y
RUN pip install --no-cache -r requirments.txt
COPY .env .
CMD ["python", "bot.py"]
