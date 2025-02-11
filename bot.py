import os
import logging
import yt_dlp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Muhit o'zgaruvchilarini yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Telegram bot obyektini yaratish
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Yuklab olish funksiyasi
def download_media(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_file = ydl.prepare_filename(info)
        audio_file = video_file.rsplit(".", 1)[0] + ".mp3"
        
        # Audio ajratish
        os.system(f"ffmpeg -i \"{video_file}\" -q:a 0 -map a \"{audio_file}\" -y")
        
        return video_file, audio_file

# Telegram bot orqali media jo‘natish
@dp.message()
async def send_media(message: Message):
    url = message.text.strip()
    
    # Faqat YouTube havolalarini qabul qilish
    if not ("youtube.com" in url or "youtu.be" in url):
        await message.reply("❌ Iltimos, faqat YouTube havolalarini yuboring! 🔗")
        return
    
    await message.reply("⏳ Iltimos, kuting... Video va audio yuklab olinmoqda.")
    
    try:
        video, audio = download_media(url)
        
        # Videoni yuborish
        video_file = FSInputFile(video)
        await message.answer_video(video_file)
        
        # Audioni yuborish
        audio_file = FSInputFile(audio)
        await message.answer_audio(audio_file)
        
        # Fayllarni o‘chirish
        os.remove(video)
        os.remove(audio)
    
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
