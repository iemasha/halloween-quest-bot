# 🎃 Halloween Quest Bot - Проблема с деплоем на Render.com

## Контекст проекта

Создаю Telegram бота для детского Хеллоуин квеста. Бот должен:
1. Принимать фотографии от детей (задание "сфотографировать тень летучей мыши")
2. Пересылать их родителям для одобрения
3. Возвращать результат в веб-приложение

## Архитектура

- **Веб-приложение:** HTML/CSS/JS на хостинге imasha.ru
- **Telegram бот:** Python (aiogram + FastAPI) на Render.com
- **Связь:** REST API между веб-приложением и ботом

## Проблема

Не удается развернуть Python бота на Render.com из-за проблем с зависимостями.

## Логи ошибок

### Ошибка 1 (sqlite3)
```
ERROR: Could not find a version that satisfies the requirement sqlite3==3.42.0 (from versions: none)
ERROR: No matching distribution found for sqlite3==3.42.0
```

### Ошибка 2 (конфликт aiofiles)
```
ERROR: Cannot install -r requirements.txt (line 1) and aiofiles==24.1.0 because these package versions have conflicting dependencies.
The conflict is caused by:
    The user requested aiofiles==24.1.0
    aiogram 3.4.1 depends on aiofiles~=23.2.1
```

### Ошибка 3 (Pillow + Python 3.13)
```
Collecting Pillow==10.1.0
error: subprocess-exited-with-error
× Getting requirements to build wheel did not run successfully.
│ exit code: 1
KeyError: '__version__'
```

### Ошибка 4 (pydantic-core + Rust)
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Caused by: Read-only file system (os error 30)
```

## Текущий requirements.txt

```txt
# Halloween Quest Bot Dependencies
aiogram==3.2.0
aiofiles==23.2.1
aiohttp==3.8.6
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
```

## Файлы проекта

- **GitHub репозиторий:** https://github.com/iemasha/halloween-quest-bot
- **Render URL:** https://halloween-quest-bot.onrender.com
- **Веб-приложение:** https://imasha.ru

## Ключевые файлы

- `requirements.txt` - зависимости Python
- `main.py` - точка входа
- `bot.py` - логика Telegram бота
- `api.py` - FastAPI сервер
- `config.py` - конфигурация
- `database.py` - SQLite база данных

## Переменные окружения в Render

```
BOT_TOKEN = 7909656312:AAEtxP0EFV4PqmttfhHMTdCZz_pRIH9_H2I
BOT_USERNAME = imashaquestbot
API_HOST = 0.0.0.0
WEB_APP_URL = https://imasha.ru
PHOTOS_DIR = ./uploads/photos
```

## Что нужно

1. Исправить `requirements.txt` для совместимости с Python 3.13 на Render
2. Убедиться что бот запускается и отвечает на `/start`
3. Проверить что API endpoints работают

## Ограничения

- Render.com использует Python 3.13.4
- Файловая система только для чтения в некоторых местах
- Нужны только базовые зависимости для aiogram + FastAPI

---

**Помогите исправить requirements.txt и настроить деплой!** 🚀
