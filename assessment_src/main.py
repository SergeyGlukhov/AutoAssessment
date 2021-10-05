import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from assessment_src.config import CONFIG, DB_DSN
from assessment_src.models import db
from assessment_src.telebot.bot import run_bot
from assessment_src.utils import setup_logging, run_migrations

logger = logging.getLogger(__name__)


async def run_app():
    setup_logging(log_config=CONFIG["logger"])
    await db.set_bind(DB_DSN)
    run_migrations()
    bot = Bot(**CONFIG["bot"])
    dp = Dispatcher(bot, storage=MemoryStorage())
    await run_bot(dp, bot)
    await db.pop_bind().close()
