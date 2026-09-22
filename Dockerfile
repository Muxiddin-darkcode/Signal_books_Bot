FROM python:3.11-slim

WORKDIR /app

# Muhit o'zgaruvchilari
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PORT=8000

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko'chirish
COPY . .

# Ma'lumotlar bazasi (SQLite) fayllarini yaratishi va yozishi uchun ruxsat
RUN chmod -R 777 /app

EXPOSE 8000

CMD ["python", "main.py"]
