import os
import logging
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram import F  # Aiogram 3 uchun kerak
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods import SendMessage
import asyncio
from dotenv import load_dotenv

# Muhit o'zgaruvchilarini yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Telegram bot obyektini yaratish
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Yuklab olish funksiyasi
def download_media(query):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        video_file = ydl.prepare_filename(info['entries'][0])
        audio_file = video_file.rsplit(".", 1)[0] + ".mp3"
        
        # Audio ajratish
        os.system(f"ffmpeg -i \"{video_file}\" -q:a 0 -map a \"{audio_file}\" -y")
        return video_file, audio_file

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Salom! Video yoki qo‘shiq nomini yozing.")

@dp.message()
async def send_media(message: Message):
    query = message.text
    await message.reply("⏳ Iltimos, kuting... Video va audio yuklab olinmoqda.")
    
    try:
        video, audio = download_media(query)
        
        # Videoni yuborish
        await message.answer_video(FSInputFile(video))
        
        # Audioni yuborish
        await message.answer_audio(FSInputFile(audio))
        
        # Fayllarni o‘chirish
        os.remove(video)
        os.remove(audio)
    except Exception as e:
        await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

