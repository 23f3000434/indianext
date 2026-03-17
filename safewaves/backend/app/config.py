import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "safewaves API"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "models")


settings = Settings()
