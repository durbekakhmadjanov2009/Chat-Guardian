from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import yt_dlp

BOT_TOKEN = "8390049742:AAERV1JhkDatnw69WrQKaKYrNJHjQFGz_s4"  # 🔹 Bot tokeningizni yozing

# ❌ Taqiqlangan so‘zlar ro‘yxati
BAD_WORDS = [
    # O‘zbekcha
    "ahmoq", "telba", "jinni", "sokin", "haqorat", "axmoq", "nodon", "la'nat", "shayton", "it", "yaramas", "beodob",
    "harom", "haromi", "bosqinchi", "sharshara", "yaramas", "lanj", "iflos", "tentak",

    # Ruscha
    "дурак", "идиот", "тупой", "баран", "осёл", "сволочь", "тварь", "мразь", "гнида", "ублюдок", "мудак",
    "пидор", "блядь", "сука", "шлюха", "проститутка", "хуй", "ебанат", "гондон", "чмо", "дерьмо", "козел",

    # Inglizcha
    "idiot", "stupid", "dumb", "fool", "loser", "bastard", "moron", "jerk", "shit", "fuck", "fucker",
    "motherfucker", "mf", "asshole", "bitch", "whore", "slut", "dick", "cock", "pussy", "cunt", "nigger",
    "retard", "gay", "fag", "faggot", "wanker"
]
  # 🔹 O'zingiz sozlashingiz mumkin

# 📊 Guruh a’zolari sonini chiqarish
async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"👥 Guruh a'zolari soni: {count}")

# 🔹 Instagram, YouTube, TikTok linklarni yuklash
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

    # 🔎 Instagram / YouTube / TikTok linklarni aniqlash
    link_regex = r"(https?:\/\/(?:www\.)?(instagram\.com|tiktok\.com|youtube\.com|youtu\.be)[^\s]+)"
    match = re.search(link_regex, text)

    if match:
        url = match.group(0).split("?")[0]  # Query qismini olib tashlaymiz
        try:
            await update.message.reply_text("📥 Yuklanmoqda...")

            ydl_opts = {
                "format": "best",
                "quiet": True,
                "noplaylist": True,
            }

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

# 🔹 Botni ishga tushirish
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("👋 Salom, men guruh moderator botman! 🚀")))
    app.add_handler(CommandHandler("members", members))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
