from pathlib import Path
import os 
import ast
from dotenv import load_dotenv
load_dotenv(override=True)
from src.logger import setup_logger
from pathlib import Path
SOURCE_PATH = Path(os.environ.get("SOURCE_DIR", "."))
SUPPORT_FORMAT = ast.literal_eval(os.environ.get("FORMATS", "['.txt']"))

## setup output dir.
OUTPUT_PATH = Path(os.environ.get("OUTPUT_DIR","output_dir"))
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Setup logger.
LOGGER = setup_logger(
    name="etl_app",
    log_dir=Path(os.environ.get("LOG_DIR","logs")),
    log_prefix="SEVEN_SIX_ETL",
    level=20,  # INFO
)