from src.logger import setup_logger
from pathlib import Path
import os
# Setup logger.
log_dir = Path(os.environ.get("LOG_DIR","logs"))
logger = setup_logger(
    name="etl_app",
    log_dir=log_dir,
    log_prefix="docling_conversion",
    level=20,  # INFO
)
## setup output dir.
output_path = Path(os.environ.get("OUTPUT_DIR","output_dir"))
output_path.mkdir(parents=True, exist_ok=True)

from src.file_loader import load_files_by_format
from src.docling_controller import build_docling_converter, convert_documents
from src.txt_extraction import text_to_md
import ast
from dotenv import load_dotenv
load_dotenv(override=True)


def main():
    # List to collect failed file paths
    failed_files = []

    # Define the folder path and file formats to load
    folder_path = Path(os.environ.get("SOURCE_DIR","."))
    formats = ast.literal_eval(os.environ.get("FORMATS",['.txt'] )) # supported format {'csv', 'docx', 'html', 'asciidoc', 'md', 'image', 'pdf', 'pptx', 'xlsx'}
    
    # Load files by format
    try:
        files = load_files_by_format(folder_path, formats)
        logger.info(f"Found {len(files)} files matching formats {formats} in {folder_path}")
        for f in files:
            logger.info(f"File found: {f}")
    except Exception as e:
        logger.error(f"Error loading files: {e}")
        return

    # Build docling converter
    doc_converter = build_docling_converter()
    docling_extensions = {
        fmt.name.lower() for fmt in doc_converter.allowed_formats
    }

    # Process each file
    for file_path in map(Path, files):
        ext = file_path.suffix.lower().lstrip(".")
        logger.info(f"Processing file: {file_path.name} with extension: {ext}")

        converted = False

        # Check if Docling supports this format
        if ext in docling_extensions:
            try:
                
                convert_documents([file_path],output_path)
                logger.info(f"File converted by Docling: {file_path.name}")
                converted = True
            except Exception as e:
                logger.warning(f"Docling failed for {file_path.name}. Reason: {e}")
                failed_files.append(str(file_path))

        # Custom logic for TXT
        if not converted:
            if ext == "txt":
                output_path_dir = output_path/ f"{file_path.stem}.md"
                try:
                    text_to_md(file_path,output_path_dir )
                    logger.info(f"File converted by custom TXT converter: {file_path.name}")
                    converted = True
                except Exception as e:
                    logger.error(f"Failed to convert TXT file {file_path.name}. Error: {e}")
                    failed_files.append(str(file_path))
            else:
                logger.warning(f"No converter available for file: {file_path.name}")
                failed_files.append(str(file_path))

    # Write failed files to file
    if failed_files:
        fail_log_path = log_dir / "failed_files.txt"
        fail_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fail_log_path, "w", encoding="utf-8") as f:
            for item in failed_files:
                f.write(f"{item}\n")
        logger.info(f"Finished: Failed files written to {fail_log_path}")
    else:
        logger.info("All files converted successfully. No failures logged.")

if __name__ == "__main__":
    main()
