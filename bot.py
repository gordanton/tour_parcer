import logging
import sqlite3

import telebot
from telebot import types

from config import ADMIN_ID, BOT_TOKEN, DB_NAME
from database import get_promotions, init_db, register_user, save_promotions
from parser import collect_all_promotions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)
init_db()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие и регистрация пользователя."""
    register_user(message.from_user)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('/promo', '/help')
    if message.from_user.id == ADMIN_ID:
        markup.row('/update', '/stats')

    welcome_text = """
✈️ <b>Travel Deals Bot</b> ✈️

Я собираю горящие туристические предложения с:
- Coral Travel
- Anex Tour
- Sunmar
- Библио-Глобус
- PEGAS Touristik
- FUN&SUN

Используйте кнопки ниже или команды:
/promo - Показать горящие предложения
/help - Помощь по боту
"""
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=markup,
    )


@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
ℹ️ <b>Помощь по боту</b>

<b>Основные команды:</b>
/promo - Показать 10 горящих предложений
/update - Обновить базу предложений (только для админа)
/stats - Статистика (только для админа)

Бот парсит сайты по команде /update.
"""
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(commands=['promo'])
def send_promotions(message):
    try:
        promotions = get_promotions(10)
        if not promotions:
            bot.send_message(
                message.chat.id,
                "⏳ В базе пока нет предложений. "
                "Попробуйте позже или запросите обновление у администратора.",
            )
            return

        response = "🔥 <b>Горящие туристические предложения</b> 🔥\n\n"
        for idx, (_, title, link, source) in enumerate(promotions, 1):
            response += (
                f"{idx}. <b>{title}</b>\n"
                f"🔗 <a href='{link}'>Подробнее</a>\n"
                f"🏷️ Источник: {source}\n\n"
            )

        bot.send_message(
            message.chat.id,
            response,
            parse_mode='HTML',
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.error("Ошибка отправки предложений: %s", exc)
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Попробуйте позже.")


@bot.message_handler(commands=['update'])
def handle_update(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав для этой команды.")
        return

    msg = bot.send_message(message.chat.id, "🔄 Начинаю обновление базы данных...")
    try:
        all_promotions = collect_all_promotions()
        count = save_promotions(all_promotions)
        if count > 0:
            bot.edit_message_text(
                f"✅ База обновлена! Добавлено {count} предложений.",
                message.chat.id,
                msg.message_id,
            )
        else:
            bot.edit_message_text(
                "⚠️ Не удалось получить новые предложения. Проверьте логи.",
                message.chat.id,
                msg.message_id,
            )
    except Exception as exc:
        logger.error("Ошибка обновления: %s", exc)
        bot.edit_message_text(
            "❌ Ошибка при обновлении. Подробности в логах.",
            message.chat.id,
            msg.message_id,
        )


@bot.message_handler(commands=['stats'])
def handle_stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав для этой команды.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM promotions")
    total_promos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT source, COUNT(*) FROM promotions GROUP BY source")
    sources = cursor.fetchall()
    conn.close()

    stats_text = f"""
📊 <b>Статистика бота</b>

Всего предложений: {total_promos}
Всего пользователей: {total_users}

<b>По источникам:</b>
"""
    for source, count in sources:
        stats_text += f"\n{source}: {count}"

    bot.send_message(message.chat.id, stats_text, parse_mode='HTML')


if __name__ == "__main__":
    logger.info("Бот запущен")
    bot.infinity_polling()
