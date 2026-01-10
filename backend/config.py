# import os
# from datetime import timedelta
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2023'
#     JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2023'
#     JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
#     # Database
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///edu2job.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     # Google OAuth
#     GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
#     GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))   # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)                # project root

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2023'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2023'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # ✅ ABSOLUTE database path (instance/edu2job.db at project root)
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f"sqlite:///{os.path.join(PROJECT_ROOT, 'instance', 'edu2job.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')