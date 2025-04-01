# Используем официальный базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt /app
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в рабочую директорию
COPY /app /app
COPY hosts.json /app 
COPY users.json /app

# Открываем порт, на котором запускается Flask (по умолчанию 5000)
EXPOSE 5000

# Запускаем приложение (например, сервер.py)
CMD ["python", "server.py"]
