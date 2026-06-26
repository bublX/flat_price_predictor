import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import BOT_TOKEN
from handlers import router

logging.basicConfig(level=logging.INFO)

# Список команд для кнопки "Меню"
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="help", description="❓ Как работает бот"),
        BotCommand(command="info", description="📊 О модели"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await set_commands(bot)  # регистрируем меню
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())