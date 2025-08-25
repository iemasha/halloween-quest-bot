# Halloween Quest Telegram Bot

Telegram бот для проверки фотографий заданий в Хеллоуин квесте.

## Функции

- 🔗 **Связывание родителя с ребенком** через QR-код
- 📸 **Получение фотографий** заданий для проверки  
- ✅ **Одобрение/отклонение** выполненных заданий
- 💬 **Комментарии** для детей от родителей
- 🌐 **REST API** для интеграции с веб-приложением

## Установка

### 1. Создать Telegram бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям, выберите имя и username бота
4. Скопируйте токен бота

### 2. Установить зависимости

```bash
cd telegram-bot
pip install -r requirements.txt
```

### 3. Настроить переменные окружения

Создайте файл `.env`:

```bash
BOT_TOKEN=7909656312:AAEtxP0EFV4PqmttfhHMTdCZz_pRIH9_H2I
BOT_USERNAME=imashaquestbot
API_HOST=0.0.0.0
API_PORT=8080
WEB_APP_URL=https://imasha.ru
PHOTOS_DIR=./uploads/photos
```

### 4. Конфигурация веб-приложения

Конфигурация веб-приложения уже обновлена с правильным username бота: `imashaquestbot`

## Запуск

### Запуск бота и API сервера

```bash
python main.py
```

### Только бот

```bash
python bot.py
```

### Только API сервер

```bash
python api.py
```

## API Endpoints

### `GET /api/check-parent-link/{session_id}`
Проверяет, привязан ли родитель к сессии

**Response:**
```json
{
  "linked": true,
  "parent_name": "Мама"
}
```

### `POST /api/upload-photo`
Загружает фото для проверки родителем

**Form Data:**
- `session_id`: ID сессии ребенка
- `task_id`: ID задания
- `task_name`: Название задания  
- `photo`: Файл изображения

**Response:**
```json
{
  "success": true,
  "submission_id": "uuid",
  "message": "Photo uploaded and sent to parent for review"
}
```

### `GET /api/photo-status/{submission_id}`
Получает статус проверки фото

**Response:**
```json
{
  "status": "approved",
  "comment": "Отличная работа!",
  "reviewed_at": "2024-10-31T15:30:00Z"
}
```

## Структура базы данных

### `family_links`
- `child_session_id` - ID сессии ребенка
- `parent_chat_id` - Telegram chat_id родителя
- `parent_username` - Username родителя в Telegram
- `linked_at` - Время связывания

### `photo_submissions`
- `submission_id` - Уникальный ID отправки
- `child_session_id` - ID сессии ребенка
- `task_id` - ID задания
- `photo_url` - Публичная ссылка на фото
- `status` - Статус: pending/approved/rejected
- `parent_comment` - Комментарий родителя

## Workflow

1. **Связывание:**
   - Ребенок сканирует QR-код
   - Родитель попадает в бота по ссылке с session_id
   - Бот создает связь в БД

2. **Отправка фото:**
   - Ребенок загружает фото через веб-приложение
   - API сохраняет фото и отправляет боту
   - Бот пересылает фото родителю с кнопками

3. **Проверка:**
   - Родитель одобряет/отклоняет через кнопки
   - Может добавить комментарий
   - Статус обновляется в БД
   - Веб-приложение получает результат

## Деплой на сервер

### С помощью systemd (Linux)

1. Создайте файл `/etc/systemd/system/halloween-bot.service`:

```ini
[Unit]
Description=Halloween Quest Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/telegram-bot
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Запустите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable halloween-bot
sudo systemctl start halloween-bot
```

### С помощью Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## Логи и отладка

Бот ведет логи всех операций:
- Создание связей
- Отправка фото
- Одобрение/отклонение
- Ошибки API

Для отладки используйте:
```bash
python main.py 2>&1 | tee bot.log
```
