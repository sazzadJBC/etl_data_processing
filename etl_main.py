import ast
from dotenv import load_dotenv
load_dotenv(override=True)
from config import LOGGER
from src.pipeline import ETLPipeline
from pathlib import Path
import os

class Main:
    def __init__(self):
        # Initialize the ETL pipeline
        self.etl_pipeline = ETLPipeline()

    def run(self):
        # Run the ETL pipeline
        self.etl_pipeline.run()


if __name__ == "__main__":
    Main().run()
    LOGGER.info("ETL pipeline completed successfully.")
