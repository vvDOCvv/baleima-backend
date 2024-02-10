from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from routers import auth, user, basic
from admin_front.admin_routers import admin_route
from contextlib import asynccontextmanager
from database.models import Base
from database.base import engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

application = FastAPI(lifespan=lifespan)

# app = FastAPI()
application.mount("/static", StaticFiles(directory="static"), name="static")


application.include_router(basic.router)
application.include_router(auth.router)
application.include_router(user.router)
application.include_router(admin_route.router)


