from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from routers.admin import admin
from routers import auth, user


from contextlib import asynccontextmanager
from database.models import Base
from database.base import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(lifespan=lifespan)


# app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)


