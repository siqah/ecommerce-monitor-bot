import os 
from pathlib import Path 
from dataclasses import dataclass 
from dotenv import load_dotenv 

load_dotenv()

@dataclass 
class Settings:
    #Bot Settings
    HEADLESS: bool = os.getenv("HEADLESS", "False").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "100"))
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30000"))

    #Email setting fo alerts
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")  

    #Monitoring settings
    CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL", "60"))
    MAX_MONITOR_CYCLES: int = int(os.getenv("MAX_CYCLES", "24"))

    #paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    SCREENSHOTS_DIR: Path = DATA_DIR / "screenshots"
    LOGS_DIR: Path = DATA_DIR / "logs"

    @classmethod 
    def setup_directories(cls):
        """"Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir( exist_ok=True)
        cls.SCREENSHOTS_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

