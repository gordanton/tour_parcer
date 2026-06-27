🧳 Travel Promotions Bot
Telegram-бот для автоматического сбора горящих туристических предложений и акций с сайтов ведущих туроператоров. Бот парсит страницы акций, сохраняет предложения в базу данных и выдаёт их пользователям по запросу с удобной пагинацией и инлайн-кнопками.

✨ Возможности
Сбор предложений с сайтов:

Coral Travel

Anex Tour

Sunmar

Библио‑Глобус

PEGAS Touristik

FUN&SUN (бывший TUI)

Пагинация – список разбит на страницы по 10 предложений, листайте вперёд/назад с помощью кнопок под сообщением.

Административные команды:

/update – принудительно обновить базу (парсинг всех источников)

/stats – статистика: общее количество предложений и пользователей

Автоматическое сохранение в SQLite – данные всегда свежие после обновления.

Логирование – все действия бота записываются для отладки.

🛠 Технологический стек
Python 3.8+

pyTelegramBotAPI – взаимодействие с Telegram Bot API

BeautifulSoup4 + requests – парсинг HTML-страниц

SQLite3 – локальное хранение данных

python-dotenv – безопасное управление переменными окружения

🚀 Установка и запуск
1. Клонируйте репозиторий
bash
git clone https://github.com/gordanton/tour_parcer.git
cd tour_parcer
2. Создайте и активируйте виртуальное окружение
bash
python3 -m venv venv
source venv/bin/activate   # для Linux/Mac
# или venv\Scripts\activate для Windows
3. Установите зависимости
bash
pip install -r requirements.txt
4. Настройте переменные окружения
Создайте файл .env в корне проекта со следующим содержимым:

env
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_ID=ваш_телеграм_id_числом
DB_NAME=travel_promotions.db
Токен получите у @BotFather

Свой ID узнайте у @userinfobot

5. Запустите бота
bash
python bot.py
При первом запуске автоматически создадутся таблицы в базе данных.

📱 Команды бота
Команда	Описание
/start	Приветственное сообщение и главное меню
/promo	Вывести первые 10 горящих предложений с кнопками пагинации
/help	Справка по командам
/update	Обновить базу данных (только для администратора)
/stats	Показать статистику (только для администратора)
После выполнения /promo под сообщением появляются кнопки ◀️ Назад и Вперед ▶️ для перелистывания.

🐧 Деплой на сервер (Timeweb / VPS)
1. Установите Python и Git
bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
2. Клонируйте репозиторий и настройте окружение
bash
cd /root
git clone https://github.com/gordanton/tour_parcer.git tour_parcer_bot
cd tour_parcer_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3. Создайте файл .env с секретами
bash
nano .env
# вставьте свои BOT_TOKEN, ADMIN_ID, DB_NAME
4. Настройте systemd-сервис для автозапуска
Создайте файл /etc/systemd/system/tour_parcer_bot.service:

ini
[Unit]
Description=Travel Promotions Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/tour_parcer_bot
ExecStart=/root/tour_parcer_bot/venv/bin/python /root/tour_parcer_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Затем:

bash
systemctl daemon-reload
systemctl enable tour_parcer_bot.service
systemctl start tour_parcer_bot.service
5. Проверьте статус
bash
systemctl status tour_parcer_bot.service
journalctl -u tour_parcer_bot.service -f
📁 Структура проекта
text
tour_parcer/
├── bot.py              # Основной код бота, обработчики команд и пагинация
├── config.py           # Загрузка переменных из .env
├── database.py         # Работа с SQLite (инициализация, сохранение, чтение)
├── parser.py           # Парсеры сайтов (универсальная функция + специфичные)
├── requirements.txt    # Список зависимостей
├── .env                # Конфиденциальные настройки (не попадает в Git)
├── .env.example        # Пример файла .env
└── README.md           # Этот файл
🤝 Как внести вклад
Форкните репозиторий.

Создайте ветку с новым функционалом.

Внесите изменения и отправьте Pull Request.

Сообщайте об ошибках через Issues.

Этот проект предназначен для образовательных целей. Используйте его ответственно и уважайте robots.txt и условия использования парсируемых сайтов.