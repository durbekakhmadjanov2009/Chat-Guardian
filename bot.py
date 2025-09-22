from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import re
import yt_dlp
from flask import Flask, request
import os

# 🔹 Bot token va webhook URL
BOT_TOKEN = os.getenv("8390049742:AAERV1JhkDatnw69WrQKaKYrNJHjQFGz_s4")  # Railway Configdan olinadi
APP_URL = os.getenv("APP_URL")  # Railway project URL: https://<project>.up.railway.app

# ❌ Taqiqlangan so‘zlar
BAD_WORDS = [
    "ahmoq", "telba", "jinni", "axmoq", "it", "iflos",
    "дурак", "идиот", "тупой", "блядь", "сука",
    "idiot", "stupid", "fuck", "bitch", "asshole"
]

# 📊 Guruh a’zolari sonini chiqarish
async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"👥 Guruh a'zolari soni: {count}")

# 🔹 Link va so‘zlarni tekshirish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # 🚫 Taqiqlangan so‘zlarni almashtirish
    clean_text = text
    for word in BAD_WORDS:
        clean_text = re.sub(rf"\b{word}\b", "❌", clean_text, flags=re.IGNORECASE)

    if clean_text != text:
        await update.message.delete()
        await update.message.reply_text(f"{update.effective_user.first_name} xabari tozalandi: {clean_text}")
        return

    # 🔎 Instagram / YouTube / TikTok linklarni yuklash
    link_regex = r"(https?:\/\/(?:www\.)?(instagram\.com|tiktok\.com|youtube\.com|youtu\.be)[^\s]+)"
    match = re.search(link_regex, text)

    if match:
        url = match.group(0).split("?")[0]
        try:
            await update.message.reply_text("📥 Yuklanmoqda...")

            ydl_opts = {"format": "best", "quiet": True, "noplaylist": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = None
                for f in info["formats"]:
                    if f.get("ext") == "mp4" and f.get("acodec") != "none":
                        video_url = f["url"]
                        break

            if video_url:
                await update.message.reply_video(video_url, caption="🎬 Video yuklandi!")

        except Exception as e:
            print("Yuklash xatoligi:", e)
            await update.message.reply_text("❌ Video yuklab bo‘lmadi.")

# 🔹 Flask server
app_flask = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# 🔹 Handlerlar
application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("👋 Salom, men guruh moderator botman! 🚀")))
application.add_handler(CommandHandler("members", members))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

@app_flask.route("/")
def home():
    return "🤖 Bot ishlayapti!"

if __name__ == "__main__":
    import asyncio
    from telegram import Bot

    # 🔹 Webhook o‘rnatish
    bot = Bot(token=BOT_TOKEN)
    asyncio.run(bot.set_webhook(f"{APP_URL}/{BOT_TOKEN}"))

    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)
