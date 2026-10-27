import logging
import sys
from pathlib import Path

# 1. Define the absolute root directory of the project using pathlib
BASE_DIR = Path(__file__).resolve().parent

# 2. Define explicit path for our data source, SQLite database and audit log file.
DATA_PATH = BASE_DIR / "data" / "raw_data.csv"
DB_PATH = BASE_DIR / "library.db"
LOG_PATH = BASE_DIR / "pipeline_logger.log"

# 3. Defensive check: Automatically create the 'data' directtory if it doesn't exist yet
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

# 4. Instantiate our centralized logger
logger = logging.getLogger("ETLPipeline")
logger.setLevel(logging.INFO)

# 5. Configure dual-destination logging (File + Console Stream)
if not logger.handlers:
    # Define a clean, uniform log format with timestamps
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler A: Writes permanent audit logs to disk ('pipeline_logger.log')
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Handler B: Streams the exact same logs live to your terminal screen
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Register both handlers to our logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)