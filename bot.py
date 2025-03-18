# 
# Корневой модуль, в котором подключаются все роутеры и стартуется бот.
# 

import asyncio
import aiogram as ag
# Импортируем роутеры из всех модулей
from modules.simpleCommands import rt as simpleCommands_rt
from modules.inMainMenu.mainMenu import rt as mainMenu_rt
from modules.inMainMenu.improvalSuggestion import rt as improvalSuggestion_rt
from modules.inMainMenu.chancelleryOrder import rt as chancelleryOrder_rt
from modules.inMainMenu.staffDirectory import rt as staffDirectory_rt
from modules.photoId import rt as photoId_rt
from modules.incorrectMsgHandler import rt as incorrectMsgHandler_rt

async def main():
    # Получаем токен для доступа к боту
    with open("token.txt") as tokenFile:
        TOKEN = tokenFile.read().strip()
    # Создаём инстанс бота
    bot = ag.Bot(token=TOKEN)
    # Создаём инстанс диспетчера
    dp = ag.Dispatcher(storage=ag.fsm.storage.memory.MemoryStorage())
    # Подключаем роутеры из других модулей - порядок подключения важен
    dp.include_routers(
        simpleCommands_rt,
        mainMenu_rt,
        improvalSuggestion_rt,
        chancelleryOrder_rt,
        staffDirectory_rt,
        photoId_rt,
        incorrectMsgHandler_rt
    )
    # Пропускаем все накопленные сообщения и начинаем поллинг новых
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())