import os
import logging
import yt_dlp
import asyncio
import ffmpeg
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

# Videoni siqish funksiyasi
def compress_video(input_file, output_file):
    try:
        ffmpeg.input(input_file).output(output_file, vcodec='libx264', crf=28, preset='fast').run(overwrite_output=True)
        return output_file
    except Exception as e:
        logging.error(f"FFmpeg xatosi: {e}")
        return input_file

# Yuklab olish funksiyasi
def download_media(query):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        
        if "entries" in info:
            info = info["entries"][0]  # Agar bu ro‘yxat bo‘lsa, birinchi elementni olish
        
        video_file = ydl.prepare_filename(info)
        audio_file = video_file.rsplit(".", 1)[0] + ".mp3"
        
        # Audio ajratish
        os.system(f"ffmpeg -i \"{video_file}\" -q:a 0 -map a \"{audio_file}\" -y")
        
        # Videoni siqish
        compressed_video = video_file.rsplit(".", 1)[0] + "_compressed.mp4"
        compressed_video = compress_video(video_file, compressed_video)
        
        return compressed_video, audio_file, info["webpage_url"]

# Telegram bot orqali media jo‘natish
@dp.message()
async def send_media(message: Message):
    query = message.text
    await message.reply("⏳ Iltimos, kuting... Video va audio yuklab olinmoqda.")
    
    try:
        video, audio, video_url = download_media(query)
        
        # Agar video 50MB dan katta bo‘lsa, havola jo‘natish
        if os.path.getsize(video) > 50 * 1024 * 1024:
            await message.reply(f"⚠️ Video fayl hajmi 50MB dan katta! Yuklab olish uchun havola: {video_url}")
            os.remove(video)  # Videoni o‘chirish
        else:
            # Videoni yuborish
            video_file = FSInputFile(video)
            await message.answer_video(video_file)
        
        # Audioni yuborish
        audio_file = FSInputFile(audio)
        await message.answer_audio(audio_file)
        
        # Fayllarni o‘chirish
        os.remove(audio)
    
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")

# Botni ishga tushirish (asyncio orqali)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
