import logging
# --- Setup logger ---
logger = logging.getLogger("notes_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/errors.log")
file_handler.setLevel(logging.ERROR)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)