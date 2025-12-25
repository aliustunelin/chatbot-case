from loguru import logger
from datetime import datetime
import pytz
import sys
import os

class Logger:
    @staticmethod
    def setup():
        logger.remove()

        def tr_time():
            return datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")

        logger.add(
            sys.stdout,
            format="<green>{time}</green> | <level>{level}</level> | <cyan>{function}</cyan> - <level>{message}</level> | 🇹🇷 {extra[tr_time]}",
            colorize=True,
            level="INFO",
        )

        # Log klasörünü oluştur
        os.makedirs("src/logs", exist_ok=True)
        
        # Dosya loglaması - rotasyon ile
        logger.add(
            "src/logs/app.log",
            rotation="00:00",      # Günlük rotasyon (gece yarısı)
            retention="7 days",    # 7 gün saklama
            compression="zip",     # Sıkıştırma
            encoding="utf-8"
        )

        return logger.bind(tr_time=tr_time())

