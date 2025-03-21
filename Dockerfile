FROM python:3

WORKDIR /srv/corp-telegram-bot

COPY . .

RUN pip install aiogram openpyxl

CMD ["python", "bot.py"]