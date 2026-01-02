import logging
import sys

from api import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from handlers.exception_handlers import setup_exception_handlers
from utils.config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logging.info("Logger initialized")

app = FastAPI(title=config.APP_NAME, debug=config.LOCAL_DEV)
setup_exception_handlers(app)
app.include_router(router.api_router)

origins = [
    "http://localhost:3000",  # frontend
    "http://127.0.0.1:3000",
    # add more later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {
        "app_name": config.APP_NAME,
        "local_dev": config.LOCAL_DEV,
    }
