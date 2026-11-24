import os
import asyncio
import re
import tempfile
from aiogram import Bot, Dispatcher, types, F
import yt_dlp

# ТОКЕН БЕРЕТСЯ ИЗ НАСТРОЕК СЕРВЕРА (МЫ НАСТРОИМ ЭТО ПОЗЖЕ)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

URL_PATTERN = re.compile(
    r'(https?://(?:www\.)?(?:instagram\.com/reel/|youtube\.com/shorts/|youtu\.be/)[^\s]+)'
)

def download_video(url: str, output_path: str):
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@dp.message(F.text.regexp(URL_PATTERN))
async def handle_link(message: types.Message):
    match = URL_PATTERN.search(message.text)
    if not match:
        return
    
    url = match.group(1)
    status_msg = await message.reply("⏳ Скачиваю видео...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "video.mp4")
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, download_video, url, temp_file_path)
            
            if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                file_size = os.path.getsize(temp_file_path) / (1024 * 1024)
                if file_size > 49:
                    await status_msg.edit_text(f"⚠️ Видео слишком большое ({file_size:.1f} МБ).")
                    return

                video_file = types.FSInputFile(temp_file_path)
                await message.reply_video(video=video_file, caption="✅ Готово!")
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Не удалось скачать видео.")
                
        except Exception as e:
            print(f"Ошибка: {e}")
            await status_msg.edit_text("❌ Ошибка при скачивании.")

async def main():
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())