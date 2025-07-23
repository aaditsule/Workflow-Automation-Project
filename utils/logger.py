import logging
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("report_mailer")
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler("logs/app.log", mode='a', encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Avoid adding handlers multiple times
    if not logger.hasHandlers(): 
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info("=== Logger Initialized ===")

    return logger

