import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.postgres import engine as pg_engine, Base as PgBase
from app.database.mysql import engine as mysql_engine, Base as MysqlBase
from app.database.mongodb import get_mongo_db, close_mongo_client
from app.database.redis_client import init_redis, close_redis

from app.api import products, orders, events, health, auth

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    
    # Init PG tables
    async with pg_engine.begin() as conn:
        await conn.run_sync(PgBase.metadata.create_all)
        
    # Init MySQL tables
    async with mysql_engine.begin() as conn:
        await conn.run_sync(MysqlBase.metadata.create_all)
        
    # Init Redis
    await init_redis()
    
    # Init Mongo
    get_mongo_db()
    
    yield
    
    logger.info("Shutting down application...")
    await pg_engine.dispose()
    await mysql_engine.dispose()
    await close_redis()
    close_mongo_client()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

app.include_router(health.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(events.router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api/docs")
