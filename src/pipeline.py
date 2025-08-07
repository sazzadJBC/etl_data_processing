from pathlib import Path
from src.logger import setup_logger
from src.db_conversion.struct_to_sql import StructuredToSQL
from src.file_loader import FileLoader
from config import SOURCE_PATH, SUPPORT_FORMAT, OUTPUT_PATH
from src.docling_extractor import DoclingConverter
from src.weaviate_utils import WeaviateClient
from src.agentic_extractor import AgenticExtractor

import os
from pathlib import Path
class ETLPipeline:
    def __init__(self, db_path: str = "business_data.db",
                 use_dask: bool = False,agentic_parse: bool = False, weaviate_collection_name:str="Business_data_collection",threshold_mb: int = 100):
        """
        Initialize the ETL Pipeline.
        :param source_path: Path where source files are located.
        :param support_format: List of supported file extensions.
        :param db_path: Path to the output database file.
        :param use_dask: Whether to use Dask for processing.
        :param agentic_parse: Whether to use Agentic Doc for parsing PDF files.
        :param weaviate_collection_name: Name of the Weaviate collection to use.
        :param threshold_mb: File size threshold (MB) for using Dask.
        """
        self.logger = setup_logger("etl_app")

        self.db_path = db_path
        self.use_dask = use_dask
        self.threshold_mb = threshold_mb
        self.agentic_parse = agentic_parse
        self.file_loader = FileLoader(directory_path=SOURCE_PATH, allowed_extensions=SUPPORT_FORMAT)
        self.struct_converter = StructuredToSQL(db_path=self.db_path, use_dask=self.use_dask, threshold_mb=self.threshold_mb)
        self.client = WeaviateClient(collection_name=weaviate_collection_name)
        self.doc_converter = DoclingConverter(self.client,self.struct_converter)
        self.agentic_extractor=AgenticExtractor()#include_marginalia=True,include_metadata_in_markdown=False, result_save_dir=OUTPUT_PATH)
        

    def run(self):
        """
        Run the ETL pipeline.
        """
        # List to collect failed file paths
        failed_files = []
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

                elif ext in [".pdf", ".docx", ".pptx", ".txt", ".md", ".html", ".asciidoc",".pptx"]:
                    self.logger.info(f"Processing document file: {file_path}")
                    if self.agentic_parse==True and ext == ".pdf":
                        # Use Agentic Doc to parse the PDF
                        result = self.agentic_extractor.parse_documents(file_path)
                        ser_result = result[0].extraction
                        print(ser_result)
                        # self.client.insert_data_from_lists(
                        #     texts=[ser_result],
                        #     sources=[file_path]
                        # )
                    else:
                        self.doc_converter.convert_documents(
                            input_paths=[file_path],  # Replace with your file paths
                            output_dir=OUTPUT_PATH,
                            table_extraction=False,
                            save_VectorDB=True,  # Enable saving to Weaviate
                            save_markdown=True,
                            save_yaml=False,
                            save_text=False,
                            save_json=False
                        )

                elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    self.logger.info(f"Processing image file: {file_path}")
                    # TODO: Add image processing here

                else:
                    self.logger.warning(f"Unsupported format: {file_path}")

            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                failed_files.append(str(file_path))

        self.struct_converter.close()
        self.logger.info("ETL pipeline completed.")
        # Write failed files to file
        if failed_files:
            fail_log_path = Path(os.environ.get("LOG_DIR","logs")/ "failed_files.txt")
            fail_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(fail_log_path, "w", encoding="utf-8") as f:
                for item in failed_files:
                    f.write(f"{item}\n")
            self.logger .info(f"Finished: Failed files written to {fail_log_path}")
        else:
            self.logger .info("All files converted successfully. No failures logged.")


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
