# Базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы requirements.txt и установим зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект Django в контейнер (с учетом подкаталога)
COPY surveysBackend /app/surveysBackend/
COPY .env /app/.env

ENV DEBUG=False

# Выполняем миграции (создаём таблицы в базе данных)
# RUN python /app/surveysBackend/manage.py makemigrations
# RUN python /app/surveysBackend/manage.py migrate

# Экспонируем порт, на котором будет работать Gunicorn
EXPOSE 8000

# Запускаем приложение через Gunicorn
CMD ["gunicorn", "--chdir", "surveysBackend", "surveysBackend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]