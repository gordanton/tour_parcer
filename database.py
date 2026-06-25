import sqlite3
import logging
from config import DB_NAME

logger = logging.getLogger(__name__)


def init_db():
    """Создает таблицы, если их нет."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("База данных инициализирована")


def save_promotions(promotions_list):
    """Сохраняет список предложений, очищая таблицу перед записью."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promotions")
    for promo in promotions_list:
        cursor.execute(
            "INSERT INTO promotions (title, link, source) VALUES (?, ?, ?)",
            (promo['title'], promo['link'], promo['source'])
        )
    conn.commit()
    conn.close()
    logger.info(f"Сохранено {len(promotions_list)} предложений")
    return len(promotions_list)


def get_promotions(limit=10):
    """Возвращает последние limit предложений."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, link, source
        FROM promotions
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


def register_user(user):
    """Регистрирует пользователя (или обновляет его данные)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    """, (user.id, user.username, user.first_name, user.last_name))
    conn.commit()
    conn.close()
