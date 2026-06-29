import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    META_VERIFICATION_TOKEN: str = os.getenv("META_VERIFICATION_TOKEN")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "1185917261267973") 
    DOWNLOADS_DIR: str = os.getenv("GEMINI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

settings = Settings()