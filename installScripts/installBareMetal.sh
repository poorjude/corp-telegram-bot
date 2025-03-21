#!/bin/bash

# устанавливаем библиотеки и код бота
pip install aiogram openpyxl
git clone https://github.com/poorjude/corp-telegram-bot

# вводим токен
cd corp-telegram-bot && touch token.txt # && nano token.txt
read -p "Введите токен от бота, полученный у @BotFather: " token
echo $token > token.txt

# запускаем бота
python bot.py