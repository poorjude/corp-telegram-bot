#!/bin/bash

# проверяем, что пользователь - root
if [ $EUID -ne 0 ]; then 
    echo "Вы должны запустить скрипт от имени root (используйте sudo)!"
    exit
fi

# скачиваем код бота
git clone https://github.com/poorjude/corp-telegram-bot

# сохраняем токен
cd corp-telegram-bot && touch token.txt
read -p "Введите токен бота, полученный у @BotFather: " token
echo $token > token.txt

# создаём docker image
docker build . -t corp-telegram-bot
printf "\nБыл создан docker image с именем corp-telegram-bot.\n\n"

# запускаем контейнер
docker run -d --name=corp-telegram-bot corp-telegram-bot
printf "\nБыл создан и запущен docker-контейнер с именем corp-telegram-bot.\n"
printf "Для того чтобы посмотреть его статус, выполните: [sudo] docker ps [-a].\n\n"