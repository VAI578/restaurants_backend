import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db").replace("postgres://", "postgresql://")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    RESTAURANTS_API_URL = os.getenv(
        "RESTAURANTS_API_URL",
        "https://restaurants-backend-gffy.onrender.com/api/restaurants",
    )