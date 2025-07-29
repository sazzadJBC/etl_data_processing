from pathlib import Path
from src.logger import setup_logger
from src.db_conversion.struct_to_sql import StructuredToSQL
from src.file_loader import FileLoader
from config import SOURCE_PATH, SUPPORT_FORMAT

class ETLPipeline:
    def __init__(self, db_path: str = "business_data.db",
                 use_dask: bool = False, threshold_mb: int = 100):
        """
        Initialize the ETL Pipeline.
        :param source_path: Path where source files are located.
        :param support_format: List of supported file extensions.
        :param db_path: Path to the output database file.
        :param use_dask: Whether to use Dask for processing.
        :param threshold_mb: File size threshold (MB) for using Dask.
        """
        self.logger = setup_logger("etl_app")

        self.db_path = db_path
        self.use_dask = use_dask
        self.threshold_mb = threshold_mb
        self.file_loader = FileLoader(directory_path=SOURCE_PATH, allowed_extensions=SUPPORT_FORMAT)
        self.struct_converter = StructuredToSQL(db_path=self.db_path, use_dask=self.use_dask, threshold_mb=self.threshold_mb)

    def run(self):
        """
        Run the ETL pipeline.
        """
        files = self.file_loader.load_files()
        self.logger.info(f"Found {len(files)} files matching formats {SUPPORT_FORMAT} in {SOURCE_PATH}")

        if not files:
            self.logger.info("No files found to process. Exiting.")
            return

        self.logger.info("Starting file conversion process...")

        for file_path in files:
            ext = Path(file_path).suffix.lower()
            try:
                if ext in [".csv", ".xlsx", ".xlsm"]:
                    self.logger.info(f"Processing structured file: {file_path}")
                    self.struct_converter.process_individual_file(file_path=file_path)

                elif ext in [".pdf", ".docx", ".pptx", ".txt", ".md", ".html", ".asciidoc"]:
                    self.logger.info(f"Processing document file: {file_path}")
                    # TODO: Add document processing here

                elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    self.logger.info(f"Processing image file: {file_path}")
                    # TODO: Add image processing here

                else:
                    self.logger.warning(f"Unsupported format: {file_path}")

            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")

        self.struct_converter.close()
        self.logger.info("ETL pipeline completed.")


# Example usage:
if __name__ == "__main__":
    pipeline = ETLPipeline(
        source_path=SOURCE_PATH,
        support_format=SUPPORT_FORMAT,
        db_path="3.db",
        use_dask=True,
        threshold_mb=100
    )
    pipeline.run()
