import time
from pathlib import Path
import yaml
import json
import pandas as pd
from src.logger import setup_logger

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

from docling_core.types.doc.document import DocItemLabel

# Define which labels you DO want (exclude TABLE)
labels_to_include = {
    DocItemLabel.PARAGRAPH,
    DocItemLabel.TEXT,
    DocItemLabel.HANDWRITTEN_TEXT,
    DocItemLabel.CAPTION,
    DocItemLabel.CHART,
    DocItemLabel.DOCUMENT_INDEX,
    DocItemLabel.TITLE
    # DocItemLabel.NUMBERED_LIST,
    # DocItemLabel.IMAGE,  # optional
    # don't include DocItemLabel.TABLE
}

class DoclingConverter:
    def __init__(self):
        self.logger = setup_logger("etl_app")
        self.doc_converter = self._build_converter()

    def _build_converter(self) -> DocumentConverter:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True
        pipeline_options.do_picture_description = False
        pipeline_options.ocr_options.lang = ["ja", "en"]
        pipeline_options.do_formula_enrichment = False
        pipeline_options.force_backend_text = False
        pipeline_options.generate_picture_images = True
        pipeline_options.images_scale = 2
        pipeline_options.do_picture_classification = True
        pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=8, device=AcceleratorDevice.AUTO
        )

        return DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.IMAGE,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.PPTX,
                InputFormat.ASCIIDOC,
                InputFormat.CSV,
                InputFormat.MD,
                InputFormat.XLSX,
            ],
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                    pipeline_cls=StandardPdfPipeline,
                    backend=PyPdfiumDocumentBackend,
                ),
                InputFormat.DOCX: WordFormatOption(
                    pipeline_cls=SimplePipeline,
                ),
            },
        )

    def convert_documents(
        self,
        input_paths,
        output_dir=Path("scratch"),
        table_extraction=True,
        struct_to_sql=None,
        save_markdown=True,
        save_yaml=False,
        save_text=False,
        save_json=False,
    ):
        start_time = time.time()
        conv_results = self.doc_converter.convert_all(input_paths)

        for res in conv_results:
            stem = res.input.file.stem
            if table_extraction:
                for table_ix, table in enumerate(res.document.tables):
                    table_df: pd.DataFrame = table.export_to_dataframe()
                    print(f"## Table {table_ix}")
                    print(table_df.to_markdown())
                    if table_df.shape[0]==0 or table_df.shape[1]==0:
                        self.logger.warning(f"Empty table found in {res.input.file.name}, skipping export.")
                        continue
                    
                    # Save the table as csv
                    file_name = f"{stem}-table-{table_ix + 1}"
                    table_df = struct_to_sql._rename_duplicate_columns(table_df)
                    struct_to_sql._insert_into_sql(table_df, file_name, mode="replace")
                    if struct_to_sql:
                        self.logger.info(f"Table {table_ix + 1} processed and inserted into SQL.")
                    else:
                        self.logger.warning("No StructuredToSQL instance provided, skipping SQL insertion.")
                    # Save the table as csv
                    element_csv_filename = output_dir / f"{file_name}.csv"
                    self.logger.info(f"Saving CSV table to {element_csv_filename}")
                    table_df.to_csv(element_csv_filename)

            self.logger.info(f"✅ Document converted: {res.input.file.name}")
            self.logger.debug(res.document._export_to_indented_text(max_text_len=16))

            if save_markdown:
                md_path = output_dir / f"{stem}.md"
                if table_extraction:
                    md_text = res.document.export_to_markdown(labels=labels_to_include)
                else:
                    md_text = res.document.export_to_markdown()
                md_path.write_text(md_text, encoding="utf-8")
                self.logger.info(f"   Markdown saved → {md_path}")

            if save_text:
                txt_path = output_dir / f"{stem}.txt"
                txt_text = res.document.export_to_text()
                txt_path.write_text(txt_text, encoding="utf-8")
                self.logger.info(f"   Text saved → {txt_path}")

            if save_yaml:
                yaml_path = output_dir / f"{stem}.yaml"
                yaml_text = yaml.safe_dump(res.document.export_to_dict())
                yaml_path.write_text(yaml_text, encoding="utf-8")
                self.logger.info(f"   YAML saved → {yaml_path}")

            if save_json:
                json_path = output_dir / f"{stem}.json"
                json_text = json.dumps(res.document.export_to_dict(), ensure_ascii=False, indent=2)
                json_path.write_text(json_text, encoding="utf-8")
                self.logger.info(f"   JSON saved → {json_path}")

        self.logger.info(f"Total time taken: {time.time() - start_time:.2f} seconds")


# Example usage
if __name__ == "__main__":
    docling = DoclingConverter()
    docling.convert_documents(
        input_paths=["example.pdf"],  # Replace with your file paths
        output_dir=Path("scratch"),
        save_markdown=True,
        save_yaml=False,
        save_text=False,
        save_json=False
    )
