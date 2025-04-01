# LocalBin - Web-приложение для быстрого обмена клипбордом.

LocalBin - это Web-приложение для обменом буфера обмена внутри локальной сети.

## Функциональность

- Отправка буфера обмена через удобный веб интерфейс
- Система логинов и авторизации
- Клиентское приложение на PyQT6

## Технологии

- Python 3.8+
- Flask  3.1.0

## Установка и запуск

1. Клонировать репозиторий:
```
git clone https://github.com/Nepaletka/localbin.git
```

2. Установить зависимости:
```
pip install -r requirements.txt
```

3. Создать файл .env с необходимыми переменными окружения:
```
FLASK_ENV: production
FLASK_SECRET_KEY: mysecretkey
```

4. Отредактировать hosts.json и users.json

5. Запустить сервер:
```
cd app
python server.py
```
6. Запустить клиент:
```
cd client
python client
```

или
```
https://github.com/Nepaletka/localbin/releases/download/v1.0.0/Client.exe
```

## Структура проекта

- `server.py` - Основной файл сервера
- `sender.py` - Функция отправки буфера
- `check_user.py` - Проверка активности клиентов
- `client` - Клиентское приложение

## Лицензия

MIT 
