from aiogram.utils import executor
import handlers
from dispatcher import dp
from db import create_db


async def on_startup(dp):
    print('Starting Bot')
    await create_db()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
