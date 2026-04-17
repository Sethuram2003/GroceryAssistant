from dotenv import load_dotenv
load_dotenv()

import logging
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.mysql_database.mysql_service import get_mysql_service, close_mysql_service

from app.api.routes.healthcheck import router as health_check_router
from app.api.routes.products import router as products_router
from app.api.routes.chat import router as chat_router
from app.api.routes.category import router as category_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Application startup initialized")

    get_mysql_service()

    yield
    
    logger.info("Application shutdown")
    
    close_mysql_service()

app = FastAPI(
    title="grocery assistant API",
    description="API for grocery management and assistance",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check_router)
app.include_router(products_router)
app.include_router(chat_router)
app.include_router(category_router)
