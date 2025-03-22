#
# Модуль стадии mainMenu: является точкой входа для взаимодействия со всеми модулями,
# которые находятся в главном меню. Пользователь попадает сюда при вводе команды "/main_menu".
# Вход в главное меню затирает все имеющиеся данные и состояния FSM.
#

import aiogram as ag

import modules.common as common
# Импортируем FSM всех остальных стадий, в которые пользователи попадают через главное меню
from modules.inMainMenu.chancelleryOrder import chancelleryOrder
from modules.inMainMenu.improvalSuggestion import improvalSuggestion
from modules.inMainMenu.staffDirectory import staffDirectory

rt = ag.Router()

# Состояния конечного автомата
class mainMenu(ag.fsm.state.StatesGroup):
    choosingOption = ag.fsm.state.State()

# Клавиатура стадии mainMenu.choosingOption
MAIN_MENU_KB = ag.types.ReplyKeyboardMarkup(
    keyboard=[
        [ ag.types.KeyboardButton(text="📩 Отправить предложение по улучшению работы компании 📩") ],
        [ ag.types.KeyboardButton(text="📝 Сделать заказ канцелярии у HR 📝") ],
        [ ag.types.KeyboardButton(text="👨🏻 Справочник сотрудников 👩🏼‍🦱") ],
        [ ag.types.KeyboardButton(text="🚪 Выйти 🚪") ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder=common.STD_INPUT_FIELD_PLACEHOLDER
)

# Хэндлер команды /main_menu, входная точка любой сессии для пользователей.
# При вызове затирает данные и состояния FSM пользователя, если такие были
@rt.message(ag.filters.command.Command("main_menu"))
async def mainMenu_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    # Очищаем данные
    await state.clear()
    if not common.isUserWorkingInCompany(message.from_user.id):
        await message.answer(
            "😔 К сожалению, вас нет в списке сотрудников нашей компании. Вы не можете пользоваться этим ботом.\n\n" +
            "Если произошла ошибка, то обратитесь к HR или системному администратору компании."
        )
    else:
        await message.answer(
            "Вы перешли в главное меню. Пожалуйста, выберите один из пунктов меню ниже.", 
            reply_markup=MAIN_MENU_KB
        )
        await state.set_state(mainMenu.choosingOption)

# Клавиатура стадии improvalSuggestion.anonOrNot
IMPROVALSUGGESTION_ANONORNOT_KB = ag.types.ReplyKeyboardMarkup(
    keyboard=[
        [
            ag.types.KeyboardButton(text="Анонимно"),
            ag.types.KeyboardButton(text="С указанием ФИО")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder=common.STD_INPUT_FIELD_PLACEHOLDER
)

# Направление пользователя на соответствующую стадию в зависимости от выбранного пункта меню
@rt.message(ag.filters.StateFilter(mainMenu.choosingOption))
async def mainMenu_choosingOption_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    if message.text == "📩 Отправить предложение по улучшению работы компании 📩":
        await message.answer(
            "Вы желаете отправить предложение анонимно или указав Ваше ФИО?",
            reply_markup=IMPROVALSUGGESTION_ANONORNOT_KB
        )
        await state.set_state(improvalSuggestion.anonOrNot)
    elif message.text == "📝 Сделать заказ канцелярии у HR 📝":
        await message.answer("Пожалуйста, введите Ваше ФИО (одним сообщением).")
        await state.set_state(chancelleryOrder.enteringFullName)
    elif message.text == "👨🏻 Справочник сотрудников 👩🏼‍🦱":
        # Клавиатура стадии staffDirectory.choosingDepartment
        staffDirectory_choosingDepartment_kb = ag.types.ReplyKeyboardMarkup(
            keyboard=
                list(map(lambda dep: [ag.types.KeyboardButton(text=dep)], common.DEPARTMENTS_IN_STAFF_INFO))
                + [[ag.types.KeyboardButton(text="↩️ Вернуться назад")]],
            resize_keyboard=True,
            input_field_placeholder=common.STD_INPUT_FIELD_PLACEHOLDER
        )
        await message.answer(
            "Вы зашли в справочник сотрудников компании.\n\nПожалуйста, выберите интересующий Вас отдел.",
            reply_markup=staffDirectory_choosingDepartment_kb
        )
        await state.set_state(staffDirectory.choosingDepartment)
    elif message.text == "🚪 Выйти 🚪":
        await message.answer("Вы вышли из главного меню.")
        await common.executeCorrectEndingOfSession(message, state)
    else: # Если пользователь написал что-то некорректное
        await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)