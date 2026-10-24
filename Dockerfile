# Берем готовый Python
FROM python:3.11-slim

# Указываем рабочую папку внутри контейнера
WORKDIR /app

# Копируем список зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код сайта
COPY . .

# Открываем порт 5000 наружу
EXPOSE 5000

# Команда для запуска сайта
CMD ["python", "app.py"]