#
# Модуль стадии chancelleryOrder: сотрудники могут отправить офис-менеджеру заказ на необходимую канцелярию 
# и прочие товары. Можно заказывать несколько товаров за один раз. 
# Сделанные заказы сохраняются в таблицы Excel дважды: во "внутренней" таблице и "внешней" таблице.
# "Внутренняя" таблица обязательно хранится локально; сохраняется в служебных целях. "Внешняя" может храниться на удалённом 
# файловом сервере, предусмотрена корректная обработка случая, когда удалённый сервер недоступен; сохраняется для доступа к 
# ней офис-менеджером.
# Пользователь попадает сюда при выборе кнопки "📝 Сделать заказ канцелярии у HR 📝" в главном меню.
#

import shutil
import os.path
import datetime
import aiogram as ag

import modules.common as common

rt = ag.Router()

# Полный путь "внутренней" Excel-таблицы, в которую записываются сделанные заказы. Должна храниться локально на диске
LOCAL_CHANCELLERY_ORDER_EXCEL_FILE_PATH = r".\chancelleryOrder\internalExcel\chancelleryOrders.xlsx"
# Путь к папке, в которой будет лежать "внешняя" Excel-таблица. Может располагаться на удалённом сервере (через этот путь 
# проверяется, есть ли права на доступ к этой папке и доступен ли сервер)
SERVER_CHANCELLERY_ORDER_FOLDER_PATH = r".\chancelleryOrder\externalExcel"
# Полный путь "внешней" Excel-таблицы, которую может прочитать офис-менеджер. Может располагаться на удалённом сервере
SERVER_CHANCELLERY_ORDER_EXCEL_FILE_PATH = r".\chancelleryOrder\externalExcel\Заказы канцелярии.xlsx"

# Добавляет информацию о сделанном заказе в соответствующий Excel-файл на компьютере
def enterChancelleryOrderToExcel_Local(stateData: dict):
    # Извлекаем ФИО и отдел сотрудника из stateData, копируем/подготавливаем для передачи в другую функцию
    currOrderFullData = {}
    for i in range(len(STATE_DATA_COMMON_KEYS)):
        serviceKey = STATE_DATA_COMMON_KEYS[i][0]
        # if serviceKey not in stateData: 
        #     continue
        currOrderFullData[serviceKey] = stateData[serviceKey]

    stateDataKeys = STATE_DATA_COMMON_KEYS + STATE_DATA_PRODUCT_KEYS
    # Запускаем цикл, в котором каждый товар будем построчно добавлять в локальный excel-файл
    savedProductsArr = stateData[STATE_DATA_SAVED_PRODUCTS_KEY]
    for i in range(len(savedProductsArr)):
        savedProduct = savedProductsArr[i]
        # Извлекаем данные об отдельном заказе из savedProduct, копируем/подготавливаем для передачи в другую функцию
        for k in range(len(STATE_DATA_PRODUCT_KEYS)):
            serviceKey = STATE_DATA_PRODUCT_KEYS[k][0]
            currOrderFullData[serviceKey] = savedProduct[serviceKey]
        common.enterStateDataToExcel(currOrderFullData, stateDataKeys, LOCAL_CHANCELLERY_ORDER_EXCEL_FILE_PATH)

# Кортежи для корректной обработки данных конечного автомата: "stateData = await state.get_data()".
# STATE_DATA_<...>_KEYS содержит в себе кортежи, в каждом из которых 2 элемента: (stateDataKey, humanReadableKey).
# serviceKey - название ключа для stateData, по которому мы получаем необходимые нам данные: stateData[serviceKey],
# humanReadableKey - человекочитаемое название stateDataKey, которое отправляется (по необходимости) пользователю.
STATE_DATA_COMMON_KEYS: tuple[tuple[str, str]] = (
    ("dateAndTime", "Дата и время отправления"),
    ("fullName", "ФИО"),
    ("department", "Отдел")
)
STATE_DATA_PRODUCT_KEYS: tuple[tuple[str, str]] = (
    ("productName", "Название товара"),
    ("articleOrLink", "Артикул или ссылка"),
    ("amount", "Количество")
)

# Название ключа для stateData, по которому мы получаем массив из заказанных товаров: 
# savedProductsArr = stateData[STATE_DATA_SAVED_PRODUCTS_KEY]
STATE_DATA_SAVED_PRODUCTS_KEY = "savedProducts"

# Состояния конечного автомата
class chancelleryOrder(ag.fsm.state.StatesGroup):
    enteringFullName = ag.fsm.state.State()
    enteringDepartment = ag.fsm.state.State()
    enteringProductName = ag.fsm.state.State()
    enteringArticleOrLink = ag.fsm.state.State()
    enteringAmount = ag.fsm.state.State()
    productApproval = ag.fsm.state.State()
    orderAnotherProductOrNot = ag.fsm.state.State()
    finalApproval = ag.fsm.state.State()

@rt.message(ag.filters.StateFilter(chancelleryOrder.enteringFullName))
async def chancelleryOrder_enteringFullName_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await state.update_data(fullName=message.text)
    await message.answer("Введите название своего отдела (одним сообщением).")
    await state.set_state(chancelleryOrder.enteringDepartment)

@rt.message(ag.filters.StateFilter(chancelleryOrder.enteringDepartment))
async def chancelleryOrder_enteringDepartment_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await state.update_data(department=message.text)
    await message.answer(
        'Начинаем ввод данных нового товара. Необходимо будет ответить на 3 вопроса.'
    )
    await message.answer("1️⃣ из 3️⃣\nВведите название товара (одним сообщением).")
    await state.set_state(chancelleryOrder.enteringProductName)

@rt.message(ag.filters.StateFilter(chancelleryOrder.enteringProductName))
async def chancelleryOrder_enteringProductName_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await state.update_data(productName=message.text)
    await message.answer("2️⃣ из 3️⃣\nВведите артикул выбранного товара или ссылку на него (одним сообщением).")
    await state.set_state(chancelleryOrder.enteringArticleOrLink)

@rt.message(ag.filters.StateFilter(chancelleryOrder.enteringArticleOrLink))
async def chancelleryOrder_enteringArticleOrLink_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await state.update_data(articleOrLink=message.text)
    await message.answer("3️⃣ из 3️⃣\nВведите количество выбранного товара (одним сообщением).")
    await state.set_state(chancelleryOrder.enteringAmount)

@rt.message(ag.filters.StateFilter(chancelleryOrder.enteringAmount))
async def chancelleryOrder_enteringAmount_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    await state.update_data(amount=message.text)
    stateData = await state.get_data()
    await message.answer(
        "Вы заказали следующий товар.\n\n" + 
        common.createStringFromStateData(stateData, STATE_DATA_PRODUCT_KEYS) + 
        "Всё верно? Хотите оставить его в заказе?",
        reply_markup=common.STD_YES_OR_NO_KB,
        parse_mode="MARKDOWN"
    )
    await state.set_state(chancelleryOrder.productApproval)

@rt.message(ag.filters.StateFilter(chancelleryOrder.productApproval))
async def chancelleryOrder_productApproval_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    if message.text == common.YES_IN_STD_YES_OR_NO_KB:
        await message.answer("Текущий товар будет сохранён в Ваш заказ.")

        # Переносим данные о товаре из временных полей, находящихся напрямую в словаре stateData, 
        # в массив словарей с аналогичными полями (сам массив тоже находится в stateData)
        stateData = await state.get_data()
        savedProduct = {}
        for i in range(len(STATE_DATA_PRODUCT_KEYS)):
            serviceKey = STATE_DATA_PRODUCT_KEYS[i][0]
            savedProduct[serviceKey] = stateData[serviceKey]
        # Проверяем, существует ли уже массив сохранённых товаров, или это первый сохранённый товар
        if STATE_DATA_SAVED_PRODUCTS_KEY in stateData:
            savedProductsArr = stateData[STATE_DATA_SAVED_PRODUCTS_KEY]
            savedProductsArr.append(savedProduct)
        else:
            savedProductsArr = [savedProduct]
        # Записываем/перезаписываем массив сохранённых товаров
        await state.update_data(savedProducts=savedProductsArr)

        await message.answer("Хотите ли Вы заказать ещё один товар?", reply_markup=common.STD_YES_OR_NO_KB)
        await state.set_state(chancelleryOrder.orderAnotherProductOrNot)
    elif message.text == common.NO_IN_STD_YES_OR_NO_KB:
        # (Не вносим данные о последнем товаре в массив сохранённых товаров)
        await message.answer("Текущий товар не будет сохранен в Ваш заказ.")
        await message.answer("Хотите ли Вы заказать ещё один товар?", reply_markup=common.STD_YES_OR_NO_KB)
        await state.set_state(chancelleryOrder.orderAnotherProductOrNot)
    else: # Если пользователь написал что-то некорректное
        await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)

@rt.message(ag.filters.StateFilter(chancelleryOrder.orderAnotherProductOrNot))
async def chancelleryOrder_orderAnotherProductOrNot_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext):
    if message.text == common.YES_IN_STD_YES_OR_NO_KB:
        await message.answer(
            'Начинаем ввод данных нового товара. Необходимо будет ответить на 3 вопроса. \n\nЗаказ канцтоваров делается с сайта "komus.ru".'
        )
        await message.answer("1️⃣ из 3️⃣\nВведите название товара (одним сообщением).")
        await state.set_state(chancelleryOrder.enteringProductName)
    elif message.text == common.NO_IN_STD_YES_OR_NO_KB:
        stateData = await state.get_data()
        # Если пользователь, по итогу, не заказал ни одного товара
        if STATE_DATA_SAVED_PRODUCTS_KEY not in stateData:
            await message.answer("😔 К сожалению, вы не заказали ни одного товара. Ваш заказ не будет сохранен и отправлен.")
            await common.executeCorrectEndingOfSession(message, state)
        else:
            # Собираем сделанный заказ в одну строку для отправки
            # Записываем общие данные (ФИО, отдел)
            messageToSend = common.createStringFromStateData(stateData, STATE_DATA_COMMON_KEYS)
            # Дописываем все сохранённые товары
            savedProductsArr = stateData[STATE_DATA_SAVED_PRODUCTS_KEY]
            for i in range(len(savedProductsArr)):
                messageToSend += common.createStringFromStateData(savedProductsArr[i], STATE_DATA_PRODUCT_KEYS)
            
            await message.answer(
                "Итак, у Вас был сформирован следующий заказ.\n\n" + messageToSend + "Вы хотите отправить его офис-менеджеру?",
                reply_markup=common.STD_YES_OR_NO_KB,
                parse_mode="MARKDOWN"
            )
            await state.set_state(chancelleryOrder.finalApproval)
    else: # Если пользователь написал что-то некорректное
        await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)

@rt.message(ag.filters.StateFilter(chancelleryOrder.finalApproval))
async def chancelleryOrder_orderAnotherProductOrNot_handler(message: ag.types.Message, state: ag.fsm.context.FSMContext, bot: ag.Bot):
    if message.text == common.YES_IN_STD_YES_OR_NO_KB:
        # Сохраняем дату и время отправления
        currDateAndTime = datetime.datetime.now().strftime(r"%d-%m-%Y %H:%M:%S")
        await state.update_data(dateAndTime=currDateAndTime)

        # Собираем сделанный заказ в одну строку для отправки
        # Записываем общие данные (ФИО, отдел)
        stateData = await state.get_data()
        messageToSend = common.createStringFromStateData(stateData, STATE_DATA_COMMON_KEYS)
        # Дописываем все сохранённые товары
        savedProductsArr = stateData[STATE_DATA_SAVED_PRODUCTS_KEY]
        for i in range(len(savedProductsArr)):
            messageToSend += common.createStringFromStateData(savedProductsArr[i], STATE_DATA_PRODUCT_KEYS)

        # Отправляем сделанный пользователем заказ офис-менеджеру
        await bot.send_message(
            common.STAFF_TO_MESSAGE.officeManager,
            "📝 Был оформлен следующий заказ канцтоваров. 📝\n\n" + messageToSend,
            parse_mode="MARKDOWN"
        )
        # Сохраняем заказ во "внутренний" Excel-файл, хранящийся локально
        enterChancelleryOrderToExcel_Local(stateData)
        # Проверяем, есть ли доступ к серверу/папке, куда мы хотим скопировать "внешний" Excel-файл
        if os.path.exists(SERVER_CHANCELLERY_ORDER_FOLDER_PATH):
            # Копируем Excel-файл на сервер
            shutil.copy(LOCAL_CHANCELLERY_ORDER_EXCEL_FILE_PATH, SERVER_CHANCELLERY_ORDER_EXCEL_FILE_PATH)
            # Отправляем уведомление офис-менеджеру
            await bot.send_message(
                common.STAFF_TO_MESSAGE.officeManager,
                "Заказ был сохранен на сервер в следующий Excel-файл:\n" +
                f"`{SERVER_CHANCELLERY_ORDER_EXCEL_FILE_PATH}`",
                parse_mode="MARKDOWN"
            )
        else:
            # Отправляем уведомление офис-менеджеру
            await bot.send_message(
                common.STAFF_TO_MESSAGE.officeManager,
                "😔 К сожалению, сохранить Excel-файл с заказом на сервер не удалось. Обратитесь к системному администратору," + 
                "чтобы он проверил, работает ли файловый сервер и выданы ли серверу с телеграм-ботом права на доступ к следующей папке:\n" + 
                f"`{SERVER_CHANCELLERY_ORDER_FOLDER_PATH}`",
                parse_mode="MARKDOWN"
            )
            # Отправляем уведомление IT
            await bot.send_message(
                common.STAFF_TO_MESSAGE.IT,
                '😔 Один из пользователей только что заказывал канцелярию (пункт меню "📝 Сделать заказ канцелярии у HR 📝") ' +
                "и, к сожалению, для него не удалось сохранить Excel-файл на файловый сервер.\n\n" +
                "Проверьте, работает ли файловый сервер и выданы ли серверу с телеграм-ботом права на доступ к следующей папке файлового сервера:\n" + 
                f"`{SERVER_CHANCELLERY_ORDER_FOLDER_PATH}`"
                "\n\nНапоминаю, что локальная копия файла лежит на сервере с телеграм-ботом по следующему пути:\n"
                f"`{LOCAL_CHANCELLERY_ORDER_EXCEL_FILE_PATH}`",
                parse_mode="MARKDOWN"
            )
        await message.answer("🎉 Ваш заказ был успешно сохранен и отправлен офис-менеджеру.")
        await common.executeCorrectEndingOfSession(message, state)
    elif message.text == common.NO_IN_STD_YES_OR_NO_KB:
        await message.answer("😔 Ваш заказ не будет сохранен и отправлен.")
        await common.executeCorrectEndingOfSession(message, state)
    else: # Если пользователь написал что-то некорректное
        await message.answer(common.ANSWER_TO_INCORRECT_CHOICE_IN_KB)