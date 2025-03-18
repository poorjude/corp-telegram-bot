#
# Модуль стадии staffDirectory: здесь сотрудники могут посмотреть информацию обо всех сотрудниках в компании, а именно:
# фотографию, ФИО, должность, отдел, день рождения, телефон, почту, телеграм. Первично все сотрудники распределены по отделам,
# после выбора отдела пользователем он может выбрать конкретного сотрудника по ФИО.
# Пользователь попадает сюда при выборе кнопки "👨🏻 Справочник сотрудников 👩🏼‍🦱" в главном меню.
#

import aiogram as ag

import modules.common as common

rt = ag.Router()

# Состояния конечного автомата
class staffDirectory(ag.fsm.state.StatesGroup):
    choosingDepartment = ag.fsm.state.State()
    choosingEmployee = ag.fsm.state.State()

@rt.message(ag.filters.StateFilter(staffDirectory.choosingDepartment))
async def staffDirectory_choosingDepartment_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    if message.text == "↩️ Вернуться назад":
        await message.answer("Вы вышли из справочника сотрудников.", reply_markup=ag.types.ReplyKeyboardRemove()) 
        await common.executeCorrectEndingOfSession(message, state)
    elif message.text not in common.DEPARTMENTS_IN_STAFF_INFO: # Если пользователь написал что-то некорректное
        await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)
    elif len(common.STAFF_INFO[message.text]) == 0: # Если в выбранном отделе нет сотрудников
        await message.answer("😔 К сожалению, в выбранном отделе пока нет сотрудников. Выберите другой отдел.")
    else:
        chosenDep = message.text
        # Собираем клавиатуру со всеми пользователями в выбранном отделе
        employeeData = []
        for employee in common.STAFF_INFO[chosenDep]:
            employeeData.append([ag.types.KeyboardButton(text=employee["ФИО"])])
        employeeData.append([ag.types.KeyboardButton(text="↩️ Вернуться назад")])
        choosingEmployee_kb = ag.types.ReplyKeyboardMarkup(
            keyboard=employeeData,
            resize_keyboard=True,
            input_field_placeholder=common.STD_INPUT_FIELD_PLACEHOLDER
        )
        # Сохраняем выбранный пользователем отдел
        await state.update_data(chosenDep=chosenDep)
        await message.answer("Теперь выберите интересующего Вас сотрудника.", reply_markup=choosingEmployee_kb)
        await state.set_state(staffDirectory.choosingEmployee)

@rt.message(ag.filters.StateFilter(staffDirectory.choosingEmployee))
async def staffDirectory_choosingEmployee_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    if message.text == "↩️ Вернуться назад":
        # Клавиатура стадии staffDirectory.choosingDepartment
        staffDirectory_choosingDepartment_kb = ag.types.ReplyKeyboardMarkup(
            keyboard=
                list(map(lambda dep: [ag.types.KeyboardButton(text=dep)], common.DEPARTMENTS_IN_STAFF_INFO)) 
                + [[ag.types.KeyboardButton(text="↩️ Вернуться назад")]],
            resize_keyboard=True,
            input_field_placeholder=common.STD_INPUT_FIELD_PLACEHOLDER
        )
        await message.answer(
            "Вы вернулись к списку отделов.\n\nПожалуйста, выберите интересующий Вас отдел.",
            reply_markup=staffDirectory_choosingDepartment_kb
        )
        await state.set_state(staffDirectory.choosingDepartment)
    else:
        # "Вспоминаем" отдел, выбранный пользователем одним шагом ранее
        stateData = await state.get_data()
        chosenDep = stateData["chosenDep"]
        # Определяем, корректно ли отправленное сообщение, и если да, сразу находим нужного сотрудника
        isMsgCorrect = False
        for employee in common.STAFF_INFO[chosenDep]:
            if message.text == employee["ФИО"]:
                chosenEmployee = employee
                isMsgCorrect = True
        if not isMsgCorrect: # Если пользователь написал что-то некорректное
            await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)
        else:
            # Готовим сообщение с данными о сотруднике
            msgToSend = ""
            for field in common.KEYS_FOR_EMPLOYEE_IN_STAFF_INFO:
                if chosenEmployee[field] == "":
                    continue
                msgToSend += field + ":\n" + chosenEmployee[field] + "\n\n"
            if chosenEmployee["photo_id"] != "": # Отправляем фото сотрудника, если оно есть
                await message.answer_photo(photo=chosenEmployee["photo_id"], caption=msgToSend)
            else:
                await message.answer(msgToSend)
            await message.answer("Снова выберите интересующего Вас сотрудника.")
            # (Не меняем состояние FSM, т.к. пользователь снова должен попасть в этот хендлер)