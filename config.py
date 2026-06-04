import os
from sqlalchemy.pool import NullPool

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///creditos.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
