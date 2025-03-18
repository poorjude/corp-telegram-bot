#
# Модуль с командами, обрабатываемыми за одно сообщение (т.е. без использования FSM и прочего).
#

import aiogram as ag

rt = ag.Router()

# Хэндлер команды /start (приветственное сообщение)
@rt.message(ag.filters.command.Command("start"), ag.filters.StateFilter(None))
async def start_handler(message: ag.types.Message):
    await message.answer(
        "Привет!\n\n" +
        "Я - корпоративный телеграм-бот. Вам доступны следующие команды:\n\n" +
        "🕹 /main_menu - открывает главное меню (скорее всего, Вам сюда)\n\n" +
        "💡 /start - показывает приветственное сообщение и список команд\n" +
        "🤖 /send_my_id - отправляет Ваш ID в Телеграме\n" +
        "🌅 /send_photo_id - отправляет ID фотографии в ответ на неё"
    )

# Хэндлер команды /send_my_id (отправляет пользователю его id в Телеграме)
@rt.message(ag.filters.command.Command("send_my_id"), ag.filters.StateFilter(None))
async def sendMyId_handler(message: ag.types.Message):
    await message.answer(
        "У Вас следующий ID профиля в Телеграме:\n" + f"`{message.from_user.id}`",
        parse_mode="MARKDOWN"
    )