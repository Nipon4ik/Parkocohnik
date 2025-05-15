import config
import aiofiles
from telegram import (
    Update,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# --- Глобальные переменные ---

user_saved_addresses = {}
user_state = {}
adress_for_remove = {}

new_parking_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Новые парковки", "Добавленные парковки"],["Информация"]],
    resize_keyboard=True
)

added_address_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["Просмотр свободных мест"],
        ["Удаление из списка адресов"],
        ["Назад"]
    ],
    resize_keyboard=True
)

address_action_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["Добавить в сохранённые"],
        ["Назад"]
    ],
    resize_keyboard=True
)

city_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Москва"], ["Назад"]],
    resize_keyboard=True
)

part_city_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["ЦАО", "ВАО", "ЮВАО", "ЮАО", "ЮЗАО"],
        ["Новомосковский", "Троицкий", "ЗАО"],
        ["СЗАО", "CАO", "CВАО", "Зеленоградский AO"],
        ["Назад"]
    ],
    resize_keyboard=True
)

district_keyboard_vao = ReplyKeyboardMarkup(
    keyboard=[
        ["Вешняки", "Богородское"],
        ["Восточный", "Гольяново", "Ивановское", "Восточное Измайлово"],
        ["Измайлово", "Северное Измайлово", "Косино-Ухтомский", "Метрогородок"],
        ["Новогиреево", "Новокосино", "Перово", "Преображенское"],
        ["Соколиная гора", "Сокольники"],
        ["Назад"]
    ],
    resize_keyboard=True
)

district_keyboard_cao = ReplyKeyboardMarkup(
    keyboard=[["Арбат", "Пресненский", "Таганка"], ["Назад"]],
    resize_keyboard=True
)

district_keyboard_yuao = ReplyKeyboardMarkup(
    keyboard=[["Кузьминки", "Таганка", "Лефортово"], ["Назад"]],
    resize_keyboard=True
)

district_keyboard_novokosino = ReplyKeyboardMarkup(
    keyboard=[["Мирской проезд дом 6"]],
    resize_keyboard=True
)


# --- Обработчики событий ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.full_name
    await update.message.reply_text(
        text=f"Добро пожаловать, {name}!",
        reply_markup=new_parking_keyboard
    )


async def new_parkings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Выберите город:",
        reply_markup=city_keyboard
    )


async def choose_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Выберите город из списка:",
        reply_markup=city_keyboard
    )
    user_state[update.message.chat_id] = "choosing_city"


async def city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text

    if city == "Москва":
        async with aiofiles.open("Moscow/karta_moscow_district.png", 'rb') as photo_file:
            photo_data = await photo_file.read()

        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=photo_data
        )

        await update.message.reply_text(
            text="Выберите административный округ города:",
            reply_markup=part_city_keyboard
        )

        user_state[update.message.chat_id] = "choosing_part"
    else:
        await update.message.reply_text(
            text="Меня пока нет, но обещаю появиться.",
            reply_markup=new_parking_keyboard
        )


async def part_city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    part = update.message.text
    if part == "ВАО":
        async with aiofiles.open("Moscow/vao_images/vao_with_districts.jpg", 'rb') as photo_file:
            photo_data = await photo_file.read()

        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=photo_data
        )

        await update.message.reply_text(
            text="Выберите район в ВАО:",
            reply_markup=district_keyboard_vao
        )

        user_state[update.message.chat_id] = "choosing_district"
    else:
        await update.message.reply_text("Меня пока нет, но обещаю появиться.")


async def district_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    district = update.message.text
    if district != "Новокосино":
        await update.message.reply_text("В этом районе пока не появился :(")
    else:
        await update.message.reply_text(
            text="Выберите улицу для добавления",
            reply_markup=district_keyboard_novokosino
        )

    user_state[update.message.chat_id] = "street_select_vao"


async def street_or_saved_address_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    address = update.message.text
    state = user_state.get(user_id)

    if state == "street_select_vao":
        user_saved_addresses.setdefault(user_id, [])

        if address not in user_saved_addresses[user_id]:
            user_saved_addresses[user_id].append(address)
            await update.message.reply_text("Адрес добавлен в сохранённые.")
        else:
            await update.message.reply_text("Этот адрес уже есть в вашем списке.")

        await update.message.reply_text(
            text="Выберите действие:",
            reply_markup=new_parking_keyboard
        )
        user_state[user_id] = "start"

    elif state == "choosing_action_with_saved_adress":
        if address in user_saved_addresses.get(user_id, []):
            adress_for_remove[user_id] = address  # просто строка, не список!
            await update.message.reply_text(
                text=f"Выберите действие с адресом: {address}",
                reply_markup=added_address_keyboard
            )
            user_state[user_id] = "choosed_action"
        else:
            await update.message.reply_text("Выберите адрес из списка.")


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = user_state.get(update.message.chat_id)

    if state == "choosing_city":
        await update.message.reply_text(
            text="Выберите действие:",
            reply_markup=new_parking_keyboard
        )
        del user_state[update.message.chat_id]
    elif state == "choosed_action":
        await update.message.reply_text(
            text="Ваши сохранённые адреса:",
            reply_markup=get_saved_addresses_keyboard(update.message.chat_id)
        )
        user_state[update.message.chat_id] = "choosing_action_with_saved_adress"

    elif state == "choosing_part":
        await update.message.reply_text(
            text="Выберите город",
            reply_markup=city_keyboard
        )
        user_state[update.message.chat_id] = "choosing_city"

    elif state == "choosing_district":
        await update.message.reply_text(
            text="Выберите административный округ",
            reply_markup=part_city_keyboard
        )
        user_state[update.message.chat_id] = "choosing_part"

    elif state == "street_select_vao":
        await update.message.reply_text(
            text="Выберите район ВАО:",
            reply_markup=district_keyboard_vao
        )
        user_state[update.message.chat_id] = "choosing_district"

    else:
        await update.message.reply_text(
            text="Вы вернулись в главное меню.",
            reply_markup=new_parking_keyboard
        )


async def added_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id not in user_saved_addresses or not user_saved_addresses[user_id]:
        await update.message.reply_text("У вас пока нет сохранённых адресов.")
        return

    await update.message.reply_text(
        text="Ваши сохранённые адреса:",
        reply_markup=get_saved_addresses_keyboard(user_id)
    )
    user_state[update.message.chat_id] = "choosing_action_with_saved_adress"

async def del_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    selected_address = adress_for_remove.get(user_id)

    if selected_address and user_id in user_saved_addresses:
        try:
            user_saved_addresses[user_id].remove(selected_address)
            await update.message.reply_text(
                text=f"Адрес {selected_address} удалён из ваших сохранённых.",
                reply_markup=new_parking_keyboard
            )
            adress_for_remove[user_id].remove(selected_address)
        except ValueError:
            await update.message.reply_text("Этот адрес не найден в вашем списке.")
    else:
        await update.message.reply_text("Не удалось найти адрес для удаления.")

    user_state[user_id] = "del_ad"


def get_saved_addresses_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    addresses = user_saved_addresses.get(user_id, [])

    if not addresses:
        return ReplyKeyboardMarkup(
            keyboard=[["Назад"]],
            resize_keyboard=True
        )

    keyboard = [[addr] for addr in addresses]
    keyboard.append(["Назад"])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
from alg import detect_cars


async def get_inf_about_park_space(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    selected_address = adress_for_remove.get(user_id)
    parks_with_space = []

    if selected_address and user_id in user_saved_addresses:
        if selected_address == "Мирской проезд дом 6":
            for i in range(0, 1):
                img_path = f"Moscow/vao_images/Novokosino/Mirskoy6_{i}.jpeg"
                url = config.Mrsk_pr[i]

                # detect_cars теперь должен возвращать bool
                has_space = detect_cars(img_path, url)
                if has_space:  # если True — есть места
                    parks_with_space.append(i)

    print("Парковки с местами:", parks_with_space)

    if parks_with_space:
        async with aiofiles.open("Moscow/vao_images/Novokosino/mrsk_6.JPG", 'rb') as photo_file:
            photo_data = await photo_file.read()

        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=photo_data
        )
        text = "🚗 Свободные места найдены на парковках: "
        text += ", ".join(str(i + 1) for i in parks_with_space)
        await update.message.reply_text(text=text)
    else:
        await update.message.reply_text(
            text=f"❌ По адресу {selected_address} свободных мест не найдено."
        )

    # Удаление использованного адреса
    if user_id in adress_for_remove:
        # Убедимся, что это список
        if isinstance(adress_for_remove[user_id], list):
            if selected_address in adress_for_remove[user_id]:
                adress_for_remove[user_id].remove(selected_address)
                # Если список опустел — удалим ключ
                if not adress_for_remove[user_id]:
                    del adress_for_remove[user_id]
        else:
            # Если по ошибке там не список — удалим ключ
            del adress_for_remove[user_id]
        user_state[update.message.chat_id] = ""
        await update.message.reply_text(
            text="Выберите действие",
            reply_markup=new_parking_keyboard
        )

async def get_inf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """

        Parkovochnik — это Telegram-бот, который помогает пользователям находить свободные парковочные места в выбранных районах Москвы. Бот анализирует изображения с камер в реальном времени и сообщает, где есть доступные места для парковки.

        ---------------------------------

    Что умеет бот:

        - Показывает новые доступные парковки по районам города.
        - Позволяет выбрать город, округ, район и улицу для поиска парковок.
        - Позволяет сохранять адреса парковок в избранное.
        - Предоставляет удобный интерфейс для просмотра и удаления сохранённых адресов.
        - Проверяет наличие свободных мест по камерам, используя компьютерное зрение.
        - Отправляет фото с камеры и выводит результат анализа: есть ли свободные места или нет.

        ---------------------------------

    Как пользоваться:

        1. Нажмите "Новые парковки" и выберите город (пока поддерживается только Москва).
        2. Выберите округ, район, затем конкретный адрес (например, *Мирской проезд дом 6*).
        3. Добавьте адрес в сохранённые.
        4. Зайдите в "Добавленные парковки", выберите адрес и нажмите "Просмотр свободных места".
        5. Бот покажет вам актуальное фото и сообщит, есть ли там свободные места
    """

    await update.message.reply_text(
        text=text,
        reply_markup=new_parking_keyboard
    )


# --- Основной запуск ---

if __name__ == '__main__':
    TOKEN = config.TOKEN

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new_parkings", new_parkings))
    app.add_handler(MessageHandler(filters.Regex('^Новые парковки$'), new_parkings))
    app.add_handler(MessageHandler(filters.Regex('^Выбрать город$'), choose_city))
    app.add_handler(MessageHandler(filters.Regex('^Москва$'), city_selected))
    app.add_handler(MessageHandler(filters.Regex('^Назад$'), back))
    app.add_handler(MessageHandler(filters.Regex("^Мирской проезд дом 6$"), street_or_saved_address_selected))
    app.add_handler(MessageHandler(filters.Regex('^Добавленные парковки$'), added_addresses))
    app.add_handler(MessageHandler(filters.Regex('^Просмотр свободных мест$'), get_inf_about_park_space))
    app.add_handler(MessageHandler(filters.Regex('^Информация$'),get_inf))

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r'^(ЦАО|ВАО|ЮВАО|ЮАО|ЮЗАО|Новомосковский|Троицкий|ЗАО|СЗАО|CАO|CВАО|Зеленоградский AO)$'
            ),
            part_city_selected
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r'^(Вешняки|Гольяново|Ивановское|Богородское|Восточный|Восточное Измайлово|'
                r'Измайлово|Северное Измайлово|Косино-Ухтомский|Метрогородок|Новогиреево|'
                r'Новокосино|Перово|Преображенское|Соколиная гора|Сокольники)$'
            ),
            district_selected
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'.*Удаление из списка адресов.*'),
            del_ad
        )
    )

    print("Бот запущен...")
    app.run_polling()