import logging
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("report_mailer")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("logs/app.log", mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(file_handler)

    return logger

