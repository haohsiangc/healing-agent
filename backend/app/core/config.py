from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "療癒對話機器人 API"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "change-me-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "sqlite:///./healing_bot.db"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-latest"

    # HuggingFace
    HF_TOKEN: str = ""

    # Image Generation
    MOCK_IMAGE_GENERATION: bool = True  # set False if GPU available
    LORA_PATH: str = "./tbh368-sdxl.safetensors"

    # Meditation audio
    MEDITATION_AUDIO_PATH: str = "./static/meditation_v2.m4a"

    # Emotion settings
    EMOTION_TRIGGER_MIN_TURNS: int = 6
    AROUSAL_LOW: float = 4.7
    AROUSAL_HIGH: float = 5.4
    VALENCE_HISTORY_WINDOW: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
