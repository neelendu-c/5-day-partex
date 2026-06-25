import logging

logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("logs.log", encoding="utf-8")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)