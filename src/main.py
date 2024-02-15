from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import STATIC_DIR, ORIGINS, ALLOW_HEADERS, ALLOW_METHODS
from admin import admin_router
from user import user_router
from auth import auth_router
from athkeeper import base_router


app = FastAPI()
app.mount(str("/static"), StaticFiles(directory=str(STATIC_DIR)), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods = ALLOW_METHODS,
    allow_headers = ALLOW_HEADERS
)

app.include_router(base_router.router)
app.include_router(auth_router.router, prefix="/api")
app.include_router(user_router.router, prefix="/api")
app.include_router(admin_router.router)
