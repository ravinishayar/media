import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cleaner import auto_delete_media_task, register_group, store_media_message

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def track_media(update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in ["group", "supergroup"]:
        register_group(update.effective_chat.id)
        if update.message and (update.message.photo or update.message.video
                               or update.message.document
                               or update.message.sticker):
            store_media_message(update.message)


async def main():
    print("🚀 Starting media cleaner bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_delete_media_task,
                      "interval",
                      minutes=2,
                      args=[app.bot])
    scheduler.start()

    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.Document.ALL
            | filters.Sticker.ALL, track_media))

    print("🤖 Media cleaner bot is running...")
    await app.run_polling()


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
