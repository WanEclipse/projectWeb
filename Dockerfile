FROM python:3.9-slim

WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . .

# Устанавливаем Flask
RUN pip install flask

# Открываем порт (тот же, что указан в app.py)
EXPOSE 5001

# Запускаем приложение
CMD ["python", "app.py"]