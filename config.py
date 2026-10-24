import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://restaurants-fronted.vercel.app")
