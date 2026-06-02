import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8747694939:AAEva3DI0PxDYTxdzdsWTY4BLpCc408JlUM"
DOWNLOAD_DIR = "downloads"

def download_video(url):
    try:
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s_%(id)s.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        logger.error(f"Помилка: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Привіт! Я бот для завантаження відео.\n\n"
        "🎬 TikTok | ▶️ YouTube | 📸 Instagram | 📌 Pinterest\n\n"
        "Просто кинь посилання і я завантажу відео!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not url.startswith('http'):
        await update.message.reply_text("❌ Це не схоже на посилання. Відправ URL відео.")
        return
    
    msg = await update.message.reply_text("⏳ Завантажую...")
    
    try:
        filepath = download_video(url)
        
        if not filepath or not os.path.exists(filepath):
            await msg.edit_text("❌ Не вдалося завантажити відео. Можливо, воно приватне або посилання некоректне.")
            return
        
        await msg.edit_text("📤 Відправляю файл...")
        
        with open(filepath, 'rb') as video:
            await update.message.reply_video(
                video,
                caption="✅ Завантажено!\n\nПідтримай бота: @your_channel",
                supports_streaming=True
            )
        
        os.remove(filepath)
        await msg.delete()
        
    except Exception as e:
        logger.error(f"Помилка: {e}")
        await msg.edit_text(f"❌ Сталася помилка: {str(e)[:100]}")

async def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот запущено!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
