import ast
from dotenv import load_dotenv
load_dotenv(override=True)
from config import LOGGER
from src.pipeline import ETLPipeline
from pathlib import Path
import os
import warnings
warnings.filterwarnings("ignore")


class Main:
    def __init__(self):
        # Initialize the ETL pipeline
        self.etl_pipeline = ETLPipeline(agentic_parse=True, db_path="business_data.db", weaviate_collection_name="Business_data_collection", use_dask=False, threshold_mb=100)

    def run(self):
        # Run the ETL pipeline
        self.etl_pipeline.run()


if __name__ == "__main__":
    Main().run()
    LOGGER.info("ETL pipeline completed successfully.")
