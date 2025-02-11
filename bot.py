import os
import logging
import yt_dlp
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# ⬇ BU YERGA TOKENINGIZNI YOZING ⬇
BOT_TOKEN = "1997127715:AAFk1qjeTNlV0zj8hrxIA8skIKZQuCkjKVc"

# Telegram bot obyektini yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Yuklab olish funksiyasi
def download_media(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        video_file = ydl.prepare_filename(info['entries'][0])
        audio_file = video_file.rsplit(".", 1)[0] + ".mp3"

        # 🎵 Audio ajratish
        command = f'ffmpeg -i "{video_file}" -q:a 0 -map a "{audio_file}" -y'
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return video_file, audio_file

@dp.message_handler()
async def send_media(message: Message):
    query = message.text
    await message.reply("⏳ Iltimos, kuting... Video va audio yuklab olinmoqda.")
    
    try:
        video, audio = download_media(query)

        # 📤 Videoni yuborish
        with open(video, "rb") as vid:
            await bot.send_video(message.chat.id, vid)

        # 🎶 Audioni yuborish
        with open(audio, "rb") as aud:
            await bot.send_audio(message.chat.id, aud)

        # 🗑 Fayllarni o‘chirish
        os.remove(video)
        os.remove(audio)
    except Exception as e:
        await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")

# Botni ishga tushirish
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

