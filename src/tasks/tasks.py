import asyncio
from celery import Celery
from auto_trade.services import CheckDB
from config import REDIS_HOST, REDIS_PORT


celery = Celery("tasks", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}")

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(15.0, check_db.s(), name='check every 15')


@celery.task
def check_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_db_async())

    # asyncio.run(check_db_async())

async def check_db_async():
    check = CheckDB()
    await check.chek_new_trades_and_update_db()

celery.conf.timezone = 'UTC'





