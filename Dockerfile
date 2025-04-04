# Базовый образ — Python 3.11
FROM python:3.11

# Папка приложения внутри контейнера
WORKDIR /app

# Копируем весь код внутрь контейнера
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 5000
EXPOSE 5000

# Команда, которая запускает сервер
CMD ["python", "server.py"]
