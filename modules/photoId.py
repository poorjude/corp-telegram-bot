#
# Модуль с хендлерами команды /send_photo_id и состояний photoId.
#

import aiogram as ag
import modules.common as common

rt = ag.Router()


# Состояния конечного автомата
class photoId(ag.fsm.state.StatesGroup):
    sendingPhoto = ag.fsm.state.State()

# Хэндлер команды /send_photo_id
@rt.message(ag.filters.command.Command("send_photo_id"), ag.filters.StateFilter(None))
async def sendPhotoId_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await message.answer("Скиньте фотографию, ID которой вы хотите получить.")
    await state.set_state(photoId.sendingPhoto)

@rt.message(ag.filters.StateFilter(photoId.sendingPhoto), ag.F.photo)
async def mainMenu_choosingOption_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await message.answer(
        "Эта фотография имеет следующий ID:\n" + f"`{message.photo[-1].file_id}`",
        parse_mode="MARKDOWN"
    )
    await common.executeCorrectEndingOfSession(message, state)

# Если пользователь на стадии photoId.sendingPhoto отправил не фотографию, а что-то некорректное
@rt.message(ag.filters.StateFilter(photoId.sendingPhoto))
async def mainMenu_choosingOption_handler(message: ag.types.Message):
    await message.answer("Вам нужно отправить фотографию, а не текст или файл. Иначе я не смогу скинуть ID.")