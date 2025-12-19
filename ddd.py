import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest  # Для настройки пула соединений
import random  # Модуль для генерации случайных чисел

# Добавлены константы состояний для обработки шагов команды /top
TOP_AMMO, TOP_MATERIALS, TOP_TEA, TOP_POWDER, \
TOP_MASKS, TOP_FIRST_AID_KITS, TOP_HOODIES, TOP_BODY_ARMORS, \
TOP_ADRENALINE, TOP_ENERGY_DRINKS, TOP_CAMERAS, TOP_GRAFFITI, \
TOP_PERMACH_PAINT, TOP_BUCKET_EMULSION, TOP_BUCKET_ULTRA, SAVE_CONFIRMATION = range(16)

# Настройки находятся здесь
TOKEN = "8222858325:AAGHHnc3dYWYjUrkOnS7HABaSyVKKLgFM6o"  # Замените на свой токен
DIR = ""  # Оставьте пустым, если не используете каталог
ADMINS_ID = ["7231206509"]  # Список ID администраторов
VERSION = "🌟 Версия бота: v1.0 ✨"
STANDARD_WELCOME = "🌍 Добро пожаловать в наш мир приключений и открытий! 🌍"
TG_CHANNEL = "https://t.me/huckstersamz"

# Настройка пула соединений и таймаутов
HTTP_REQUEST_SETTINGS = {
    'connection_pool_size': 20,       # Увеличим размер пула соединений
    'read_timeout': 15,               # Увеличим таймаут чтения
    'connect_timeout': 10,            # Увеличим таймаут соединения
}

# Создаем обработчик запросов с указанным конфигом
REQUEST = HTTPXRequest(**HTTP_REQUEST_SETTINGS)

# Глобальная переменная для хранения приложения
APP = None

# Глобальные переменные для статистики
GLOBAL_STATISTICS = []

# Основные команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    if str(chat_id) in ADMINS_ID:
        await context.bot.send_message(chat_id=chat_id, text="🎖 Вы успешно вошли как администратор!")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"👋 Привет, {user.first_name}!\n{STANDARD_WELCOME}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text("📌 Доступные команды:\n"
                                    "/help - 📌 Список команд\n"
                                    "/start - 🚶 Запустить бота\n"
                                    "/profile - 👤 Посмотреть свой профиль\n"
                                    "/getid - ☆ Узнать свой уникальный ID\n"
                                    "/rank - 🏅 Уровень и опыт (В разработке)\n"
                                    "/botinfo - 🗣 Информация о боте\n"
                                    "/random - 🎲 Случайное число\n"
                                    "/chance - 🎯 Определить вероятность события\n"
                                    "/binar - 🛠 Преобразовать числа\n"
                                    "/write - 💬 Отправить сообщение от имени бота\n"
                                    "\n⭐ Администрация:\n"
                                    "/ahelp - 👉 Специальные возможности администрации")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /profile"""
    user = update.effective_user
    await update.message.reply_text(f"🖼 Ваш профиль:\n"
                                    f"🎨 Имя: {user.first_name}\n"
                                    f"☆ ID: {user.id}")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /getid"""
    user = update.effective_user
    await update.message.reply_text(f"🔢 Ваш ID: {user.id}")

async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /rank"""
    await update.message.reply_text("🕵 Система уровней и опыта временно отключена.")

async def botinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /botinfo"""
    await update.message.reply_text(f"{VERSION}\n📌 Telegram-канал: {TG_CHANNEL}")

async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /random"""
    try:
        min_val = int(context.args[0])
        max_val = int(context.args[1])
        result = random.randint(min_val, max_val)
        await update.message.reply_text(f"🎲 Случайное число между {min_val} и {max_val}: {result}")
    except Exception as e:
        await update.message.reply_text("🚫 Неправильные аргументы. Формат: /random минимум максимум")

async def chance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /chance"""
    event = ' '.join(context.args)
    if not event:
        return await update.message.reply_text("🚫 Используйте команду правильно: /chance событие")
    probability = random.randint(0, 100)  # Генерация случайного процента от 0 до 100
    await update.message.reply_text(f"🎯 Вероятность события '{event}': {probability}%")

async def binar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /binar"""
    num_str = ''.join(context.args)
    try:
        number = int(num_str, 0)
        binary_representation = bin(number)[2:]
        decimal_representation = str(int(binary_representation, 2))
        await update.message.reply_text(f"💽 Десятичный вид: {decimal_representation},\n"
                                       f"💽 Двоичный вид: {binary_representation}")
    except ValueError:
        await update.message.reply_text("🚫 Неверный ввод числа. Пример правильного ввода: /binar 10 или /binar 0b1010")

async def write(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /write"""
    message = ' '.join(context.args)
    if not message:
        return await update.message.reply_text("🚫 Используйте команду правильно: /write текст")
    await update.message.reply_text(message)

# Новая команда для сбора статистики
async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /top"""
    await update.message.reply_text('Введите количество патронов числом.')
    return TOP_AMMO

async def save_top_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сохранения статистики"""
    answer = update.message.text.strip().lower()
    current_state = context.user_data.get('state', {})

    if answer == 'да':
        now = datetime.now()  # Получаем текущую дату и время
        stats_entry = {
            'ammo': current_state.get('ammo'),
            'materials': current_state.get('materials'),
            'tea': current_state.get('tea'),
            'powder': current_state.get('powder'),
            'masks': current_state.get('masks'),
            'first_aid_kits': current_state.get('first_aid_kits'),
            'hoodies': current_state.get('hoodies'),
            'body_armors': current_state.get('body_armors'),
            'adrenaline': current_state.get('adrenaline'),
            'energy_drinks': current_state.get('energy_drinks'),
            'cameras': current_state.get('cameras'),
            'graffiti': current_state.get('graffiti'),
            'permach_paint': current_state.get('permach_paint'),
            'bucket_emulsion': current_state.get('bucket_emulsion'),
            'bucket_ultra': current_state.get('bucket_ultra'),
            'created_at': now.strftime('%Y-%m-%d %H:%M:%S'),  # Дата и время создания
        }
        GLOBAL_STATISTICS.append(stats_entry)
        await update.message.reply_text("✅ Статистика успешно сохранена!")
    else:
        await update.message.reply_text("❌ Сохранение отменено. Повторите попытку позже.")

    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена текущего процесса"""
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

# Конвертация значений в цифры
async def convert_value(value: str):
    try:
        return int(value)
    except ValueError:
        raise ValueError("Некорректный ввод значения. Необходимо целое число.")

# Обработчики шагов команды /top
async def handle_ammo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['ammo'] = value
    await update.message.reply_text('Напишите количество материалов:')
    return TOP_MATERIALS

async def handle_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['materials'] = value
    await update.message.reply_text('Напишите количество зелёного чая:')
    return TOP_TEA

async def handle_tea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['tea'] = value
    await update.message.reply_text('Напишите количество мятной пудры:')
    return TOP_POWDER

async def handle_powder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['powder'] = value
    await update.message.reply_text('Напишите количество масок:')
    return TOP_MASKS

async def handle_masks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['masks'] = value
    await update.message.reply_text('Напишите количество аптечек:')
    return TOP_FIRST_AID_KITS

async def handle_first_aid_kits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['first_aid_kits'] = value
    await update.message.reply_text('Напишите количество стяжек:')
    return TOP_HOODIES

async def handle_hoodies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['hoodies'] = value
    await update.message.reply_text('Напишите количество бронежилетов:')
    return TOP_BODY_ARMORS

async def handle_body_armors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['body_armors'] = value
    await update.message.reply_text('Напишите количество адреналина:')
    return TOP_ADRENALINE

async def handle_adrenaline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['adrenaline'] = value
    await update.message.reply_text('Напишите количество энергетиков:')
    return TOP_ENERGY_DRINKS

async def handle_energy_drinks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['energy_drinks'] = value
    await update.message.reply_text('Напишите количество скрытых камер:')
    return TOP_CAMERAS

async def handle_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['cameras'] = value
    await update.message.reply_text('Напишите количество Amazing Graffiti:')
    return TOP_GRAFFITI

async def handle_graffiti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['graffiti'] = value
    await update.message.reply_text('Напишите количество краски Permach:')
    return TOP_PERMACH_PAINT

async def handle_permach_paint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['permach_paint'] = value
    await update.message.reply_text('Напишите количество ведёр с эмульсией:')
    return TOP_BUCKET_EMULSION

async def handle_bucket_emulsion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['bucket_emulsion'] = value
    await update.message.reply_text('Напишите количество ведёр с эмульсией Ultra:')
    return TOP_BUCKET_ULTRA

async def handle_bucket_ultra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await convert_value(update.message.text)
    if 'state' not in context.user_data:
        context.user_data['state'] = {}
    context.user_data['state']['bucket_ultra'] = value
    stats_output = (
        f"Патронов - {context.user_data['state'].get('ammo')}\n"
        f"Материалов - {context.user_data['state'].get('materials')}\n"
        f"Зелёного чая - {context.user_data['state'].get('tea')}\n"
        f"Мятной пудры - {context.user_data['state'].get('powder')}\n"
        f"Маски - {context.user_data['state'].get('masks')}\n"
        f"Аптечки - {context.user_data['state'].get('first_aid_kits')}\n"
        f"Стажки - {context.user_data['state'].get('hoodies')}\n"
        f"Бронежилеты - {context.user_data['state'].get('body_armors')}\n"
        f"Адреналин - {context.user_data['state'].get('adrenaline')}\n"
        f"Энергетики - {context.user_data['state'].get('energy_drinks')}\n"
        f"Скрытые камеры - {context.user_data['state'].get('cameras')}\n"
        f"Amazing Graffiti - {context.user_data['state'].get('graffiti')}\n"
        f"Краска Permach - {context.user_data['state'].get('permach_paint')}\n"
        f"Вёдра с эмульсией - {context.user_data['state'].get('bucket_emulsion')}\n"
        f"Вёдра с эмульсией Ultra - {context.user_data['state'].get('bucket_ultra')}"
    )
    await update.message.reply_text(stats_output + "\n\nСохраняем статистику? Напишите \"Да\", если сохраняем, \"Нет\" если что-то нужно редактировать.")
    return SAVE_CONFIRMATION

# Команда просмотра статистики
async def stata_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stata"""
    if len(GLOBAL_STATISTICS) > 0:
        messages = []
        for idx, entry in enumerate(GLOBAL_STATISTICS):
            created_at = entry.get('created_at')
            message = (
                f"\n📊 Статистика №{idx+1}:\n"
                f"🔫 Патронов - {entry.get('ammo')}\n"
                f"🏗️ Материалы - {entry.get('materials')}\n"
                f"🍵 Зелёного чая - {entry.get('tea')}\n"
                f"🌿 Мятной пудры - {entry.get('powder')}\n"
                f"🩹 Маски - {entry.get('masks')}\n"
                f"🩺 Аптечки - {entry.get('first_aid_kits')}\n"
                f"🧥 Стажки - {entry.get('hoodies')}\n"
                f"🥾 Бронежилеты - {entry.get('body_armors')}\n"
                f"🩸 Адреналин - {entry.get('adrenaline')}\n"
                f"🍺 Энергетики - {entry.get('energy_drinks')}\n"
                f"📷 Скрытые камеры - {entry.get('cameras')}\n"
                f"🎨 Amazing Graffiti - {entry.get('graffiti')}\n"
                f"🎨 Краска Permach - {entry.get('permach_paint')}\n"
                f"🎨 Ведра с эмульсией - {entry.get('bucket_emulsion')}\n"
                f"🎨 Ведра с эмульсией Ultra - {entry.get('bucket_ultra')}\n"
                f"📅 Дата создания: {created_at}"
            )
            messages.append(message)
        await update.message.reply_text("\n".join(messages))
    else:
        await update.message.reply_text("🧃 Пока никакой статистики нет.")

# Основная административная команда
async def ahelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /ahelp"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    await update.message.reply_text("📌 Списки специальных возможностей для администрации:\n"
                                    "/pin - 📌 Закрепить сообщение\n"
                                    "/unpin - 📌 Открепить сообщение\n"
                                    "/unpinall - 📌 Открепить все сообщения\n"
                                    "/warn - 🚫 Предупредить участника\n"
                                    "/unwarn - 🌈 Снять предупреждение\n"
                                    "/title - 🎉 Изменить название чата\n"
                                    "/description - 📄 Изменить описание чата\n"
                                    "/setwelcome - 💬 Установка нового приветственного сообщения\n"
                                    "/top - 📊 Сбор статистики ресурсов\n"
                                    "/stata - 📊 Просмотр всей собранной статистики")

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /pin"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    pinned_message = update.message.reply_to_message
    await context.bot.pin_chat_message(chat_id=update.effective_chat.id, message_id=pinned_message.message_id)
    await update.message.reply_text("📌 Сообщение закреплено.")

async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /unpin"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    await context.bot.unpin_chat_message(chat_id=update.effective_chat.id)
    await update.message.reply_text("📌 Закрепленное сообщение снято.")

async def unpinall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /unpinall"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    await context.bot.unpin_all_chat_messages(chat_id=update.effective_chat.id)
    await update.message.reply_text("📌 Все закрепленные сообщения сняты.")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /warn"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    warned_user = update.message.reply_to_message.from_user
    await update.message.reply_text(f"🚫 Участнику {warned_user.first_name} выдано предупреждение.")

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /unwarn"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    unwarned_user = update.message.reply_to_message.from_user
    await update.message.reply_text(f"🌈 Предупреждение участнику {unwarned_user.first_name} снято.")

async def title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /title"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    new_title = ' '.join(context.args)
    await context.bot.set_chat_title(chat_id=update.effective_chat.id, title=new_title)
    await update.message.reply_text(f"🎉 Название чата изменено на '{new_title}'.")

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /description"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    new_description = ' '.join(context.args)
    await context.bot.set_chat_description(chat_id=update.effective_chat.id, description=new_description)
    await update.message.reply_text(f"📄 Описание чата изменено на '{new_description}'.")

async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /setwelcome"""
    if int(update.effective_user.id) not in map(int, ADMINS_ID):
        return await update.message.reply_text("🚫 У вас недостаточно прав для выполнения этой команды.")
    new_welcome_message = ' '.join(context.args)
    global STANDARD_WELCOME
    STANDARD_WELCOME = new_welcome_message
    await update.message.reply_text(f"💬 Новый текст приветствия установлен: '{new_welcome_message}'.")

def main():
    global APP
    APP = Application.builder().token(TOKEN).request(REQUEST).build()  # Применяем обработчик запросов

    # Добавляем обработчики команд
    APP.add_handler(CommandHandler("start", start))
    APP.add_handler(CommandHandler("help", help_command))
    APP.add_handler(CommandHandler("profile", profile))
    APP.add_handler(CommandHandler("getid", getid))
    APP.add_handler(CommandHandler("rank", rank))
    APP.add_handler(CommandHandler("botinfo", botinfo))
    APP.add_handler(CommandHandler("random", random_number))
    APP.add_handler(CommandHandler("chance", chance))
    APP.add_handler(CommandHandler("binar", binar))
    APP.add_handler(CommandHandler("write", write))

    # Диалоговая обработка команды /top
    CONV_HANDLER = ConversationHandler(
        entry_points=[CommandHandler("top", top_command)],
        states={
            TOP_AMMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ammo)],
            TOP_MATERIALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_materials)],
            TOP_TEA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tea)],
            TOP_POWDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_powder)],
            TOP_MASKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_masks)],
            TOP_FIRST_AID_KITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_first_aid_kits)],
            TOP_HOODIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_hoodies)],
            TOP_BODY_ARMORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_body_armors)],
            TOP_ADRENALINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adrenaline)],
            TOP_ENERGY_DRINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_energy_drinks)],
            TOP_CAMERAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cameras)],
            TOP_GRAFFITI: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_graffiti)],
            TOP_PERMACH_PAINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_permach_paint)],
            TOP_BUCKET_EMULSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bucket_emulsion)],
            TOP_BUCKET_ULTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bucket_ultra)],
            SAVE_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_top_stats)]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)]
    )
    APP.add_handler(CONV_HANDLER)

    # Добавляем новые команды для административной панели
    APP.add_handler(CommandHandler("ahelp", ahelp))
    APP.add_handler(CommandHandler("pin", pin))
    APP.add_handler(CommandHandler("unpin", unpin))
    APP.add_handler(CommandHandler("unpinall", unpinall))
    APP.add_handler(CommandHandler("warn", warn))
    APP.add_handler(CommandHandler("unwarn", unwarn))
    APP.add_handler(CommandHandler("title", title))
    APP.add_handler(CommandHandler("description", description))
    APP.add_handler(CommandHandler("setwelcome", setwelcome))
    APP.add_handler(CommandHandler("top", top_command))   # Переносим сюда топ-команду
    APP.add_handler(CommandHandler("stata", stata_command))  # Переносим сюда стат-команду

    # Запускаем приложение
    APP.run_polling()

if __name__ == "__main__":
    main()
