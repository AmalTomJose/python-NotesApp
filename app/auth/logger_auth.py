import logging
import os

# Make sure logs folder exists
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("auth_logger")
logger.setLevel(logging.INFO)

# File handler (errors)
file_handler = logging.FileHandler("logs/errorsAuth.log")
file_handler.setLevel(logging.ERROR)

# Console handler (info)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)