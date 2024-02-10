import asyncio
from celery import Celery
from mexc.trade_services import CheckDB


celery = Celery("tasks", broker="redis://localhost:6379")

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(15.0, check_db.s(), name='add every 10')


@celery.task
def check_db():
    check = CheckDB()
    asyncio.run(check.chek_new_trades_and_update_db())


celery.conf.timezone = 'UTC'





