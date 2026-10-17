import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me any YouTube link, and I will download and send you the video file!")

async def download_youtube_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "youtube.com" not in url and "youtu.be" not in url:
        return

    await update.message.reply_text("⏳ Downloading video from YouTube, please wait...")

    output_template = "downloaded_video.%(ext)s"
    ydl_opts = {
        'format': 'mp4[height<=360]',
        'outtmpl': output_template,
        'max_filesize': 50 * 1024 * 1024,
        # Spoof an Android client to bypass bot detection on cloud servers
        'extractor_args': {'youtube': {'player_client': ['android']}},
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_text("📤 Uploading video to Telegram...")
        
        with open(filename, "rb") as video_file:
            await update.message.reply_video(video=video_file, caption=info.get('title', 'YouTube Video'))

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to process video. Error: {str(e)}")
        if os.path.exists("downloaded_video.mp4"):
            os.remove("downloaded_video.mp4")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_youtube_video))
    
    print("YouTube downloader bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
