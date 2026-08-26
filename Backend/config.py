import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///traffic.db"  # or MySQL if needed
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "novaloop_secret")
