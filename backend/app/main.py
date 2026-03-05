import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.routers import auth, chat, image, meditation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s...", settings.APP_NAME)
    init_db()
    logger.info("Database tables created/verified.")
    if settings.MOCK_IMAGE_GENERATION:
        logger.info("Image generation: MOCK mode (no GPU required)")
    else:
        logger.info("Image generation: REAL mode (SDXL will lazy-load on first request)")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(image.router)
app.include_router(meditation.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
