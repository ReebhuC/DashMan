import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    MONGO_URI = "mongodb://localhost:27017/dashman"
    SECRET_KEY = "dev"
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

