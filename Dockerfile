# Python image asosida konteyner yaratamiz
FROM python:3.12

# FFMPEG va boshqa zaruriy paketlarni o‘rnatish
RUN apt-get update && apt-get install -y ffmpeg

# Ishchi katalogni yaratamiz
WORKDIR /app

# Talab qilinadigan Python kutubxonalarini o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha fayllarni konteynerga nusxalash
COPY . .

# Botni ishga tushirish
CMD ["python", "bot.py"]
