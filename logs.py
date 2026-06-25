import logging
from logger_config import logger
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = RotatingFileHandler("errors.log", maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)