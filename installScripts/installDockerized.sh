#!/bin/bash

# проверяем, что пользователь - root
if [ $EUID -ne 0 ]; then 
    echo "Вы должны запустить скрипт от имени root (используйте sudo)!"
    exit
fi

# скачиваем код бота
git clone https://github.com/poorjude/corp-telegram-bot

# сохраняем токен
cd corp-telegram-bot && touch ./token.txt
read -p "Введите токен бота, полученный у @BotFather: " token
echo ""
echo $token > ./token.txt

# создаём docker image
docker build . -t corp-telegram-bot
printf "\nБыл создан docker image с именем corp-telegram-bot.\n\n"

# запускаем контейнер
docker run -d --name=corp-telegram-bot corp-telegram-bot
printf "\nБыл создан и запущен docker-контейнер с именем corp-telegram-bot.\n"
printf "Для того чтобы посмотреть его статус, выполните: [sudo] docker ps [-a].\n\n"

# сохраняем ID телеграм-аккаунта пользователя
echo "Откройте диалог с ботом в Телеграме и отправьте ему следующую команду:"
echo "/send_my_id"
read -p "Когда сделаете это, нажмите Enter." >> /dev/null
read -p "Теперь введите ID, которое скинул Вам бот: " tg_id
echo ""
# вставляем ID в справочник
sed -i.bak "11d" ./staffInfo/staffInfo.json
sed -i.bak '11i\            "tg_id": '$tg_id ./staffInfo/staffInfo.json
# копируем справочник в контейнер и перезапускаем контейнер
docker cp ./staffInfo/staffInfo.json corp-telegram-bot:/srv/corp-telegram-bot/staffInfo/staffInfo.json # >> /dev/null
docker restart corp-telegram-bot # >> /dev/null
printf "\nГотово! Теперь вы можете пользоваться своим ботом.\n\n"