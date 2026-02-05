from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, CONNECT_DB, ADMIN_ID
from middleware.db_middleware import DbSession
from utils.create_db import create_db
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from handlers.form import router
import psycopg_pool
import asyncio
import logging
import sys

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

async def create_pool():
    return psycopg_pool.AsyncConnectionPool(CONNECT_DB)

async def start_bot(bot: Bot):
    await bot.send_message(chat_id=ADMIN_ID, text='Bot started')

async def stop_bot(bot: Bot):
    await bot.send_message(chat_id=ADMIN_ID, text='Bot stopped')

async def start():
    await create_db()
    poolling = await create_pool()
    poolling.connection_class.autocommit = True
    dp.update.middleware.register(DbSession(poolling))
    dp.include_router(router=router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)


    asyncio.run(start())



