FROM python:3.11-slim

WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . .

# Устанавливаем Flask
RUN pip install flask

# Открываем порт (тот же, что указан в app.py)
EXPOSE 5001

# Запускаем приложение
ENTRYPOINT ["python", "app.py"]