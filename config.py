import os


DEV_SECRET_KEY = "dev-only-change-before-deployment"


def is_production():
    """True when the app runs on the live server (APP_ENV=production)."""
    return os.environ.get("APP_ENV", "").strip().lower() == "production"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", DEV_SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///noted.db"
    )
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = (
            "postgresql+psycopg://" + SQLALCHEMY_DATABASE_URI[len("postgres://"):]
        )
    elif SQLALCHEMY_DATABASE_URI.startswith("postgresql://"):
        SQLALCHEMY_DATABASE_URI = (
            "postgresql+psycopg://" + SQLALCHEMY_DATABASE_URI[len("postgresql://"):]
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
