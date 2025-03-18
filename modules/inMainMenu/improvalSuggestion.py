#
# Модуль стадии improvalSuggestion: сотрудники компании могут написать гендиректору (по умолчанию) предложение по улучшению
# работы в ней, в целом, свои идеи, впечатления, мысли. Сделать это можно как анонимно, так и с указанием ФИО.
# Пользователь попадает сюда при выборе кнопки "📩 Отправить предложение по улучшению работы компании 📩" в главном меню.
#

import datetime
import aiogram as ag

import modules.common as common

rt = ag.Router()

# Кортеж для корректной обработки данных конечного автомата: "stateData = await state.get_data()".
# STATE_DATA_KEYS содержит в себе кортежи, в каждом из которых 2 элемента: (stateDataKey, humanReadableKey).
# serviceKey - название ключа для stateData, по которому мы получаем необходимые нам данные: stateData[serviceKey],
# humanReadableKey - человекочитаемое название stateDataKey, которое отправляется (по необходимости) пользователю.
STATE_DATA_KEYS: tuple[tuple[str, str]] = (
    ("dateAndTime", "Дата и время отправления"),
    ("fullName", "ФИО"),
    ("suggestion", "Предложение")
)

# Состояния конечного автомата
class improvalSuggestion(ag.fsm.state.StatesGroup):
    anonOrNot = ag.fsm.state.State()
    enteringFullName = ag.fsm.state.State()
    enteringSuggestion = ag.fsm.state.State()
    finalApproval = ag.fsm.state.State()

@rt.message(ag.filters.StateFilter(improvalSuggestion.anonOrNot))
async def improvalSuggestion_anonOrNot_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    if message.text == "Анонимно":
        await state.update_data(fullName="Анонимно")
        await message.answer(
            "Теперь Вы можете написать свое предложение по улучшению работы компании (одним сообщением)."
        )
        await state.set_state(improvalSuggestion.enteringSuggestion)
    elif message.text == "С указанием ФИО":
        await message.answer("Пожалуйста, введите своё ФИО (одним сообщением).")
        await state.set_state(improvalSuggestion.enteringFullName)
    else: # Если пользователь написал что-то некорректное
        await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)

@rt.message(ag.filters.StateFilter(improvalSuggestion.enteringFullName))
async def improvalSuggestion_enteringFullName_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await state.update_data(fullName=message.text)
    await message.answer(
        "Теперь Вы можете написать свое предложение по улучшению работы компании (одним сообщением)."
    )
    await state.set_state(improvalSuggestion.enteringSuggestion)

@rt.message(ag.filters.StateFilter(improvalSuggestion.enteringSuggestion))
async def improvalSuggestion_enteringSuggestion_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await state.update_data(suggestion=message.text)
    stateData = await state.get_data()
    await message.answer(
        "Вы хотите отправить введённое Вами предложение?\n\n" +
        common.createStringFromStateData(stateData, STATE_DATA_KEYS),
        reply_markup=common.STD_YES_OR_NO_KB,
        parse_mode="MARKDOWN"
    )
    await state.set_state(improvalSuggestion.finalApproval)

@rt.message(ag.filters.StateFilter(improvalSuggestion.finalApproval))
async def improvalSuggestion_finalApproval_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext, bot: ag.Bot):
    if message.text == common.YES_IN_STD_YES_OR_NO_KB:
        # Сохраняем дату и время отправления
        currDateAndTime = datetime.datetime.now().strftime(r"%d-%m-%Y %H:%M:%S")
        await state.update_data(dateAndTime=currDateAndTime)
        stateData = await state.get_data()
        # Отправляем сохраненные данные в HR-отдел
        await bot.send_message(
            common.STAFF_TO_MESSAGE.HR, 
            "📩 Было отправлено следующее предложение по улучшению работы в компании. 📩\n\n" + 
            common.createStringFromStateData(stateData, STATE_DATA_KEYS),
            parse_mode="MARKDOWN"
        )
        await message.answer("🎉 Ваше предложение сохранено и отправлено в HR-отдел. Спасибо за Вашу инициативу.")
        await common.executeCorrectEndingOfSession(message, state)
    elif message.text == common.NO_IN_STD_YES_OR_NO_KB:
        await message.answer(
            "😔 Ваше предложение не будет сохранено и отправлено. Вы можете подать новое, выбрав соответствующий пункт в главном меню."
        )
        await common.executeCorrectEndingOfSession(message, state)
    else: # Если пользователь написал что-то некорректное
        await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)