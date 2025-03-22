#!/bin/bash

# проверяем, что пользователь - root
if [ $EUID -ne 0 ]; then 
    echo "Вы должны запустить скрипт от имени root (используйте sudo)!"
    exit
fi
# проверяем, что скрипт был запущен в той же директории, что и установочный скрипт
if [ ! -d "./corp-telegram-bot" ]; then 
    echo "Вы должны запустить скрипт в той же директории, в которой запускали installDockerized.sh!"
    exit
fi

# останавливаем и удаляем контейнер, удаляем созданный образ
docker stop corp-telegram-bot
docker container rm corp-telegram-bot
docker image rm corp-telegram-bot

# удаляем все данные с устройства
rm -rf ./corp-telegram-bot
rm -f ./installDockerized.sh
rm -f ./uninstallDockerized.sh

echo "corp-telegram-bot был полностью удалён с вашего устройства"