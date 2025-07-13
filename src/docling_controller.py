import time
from pathlib import Path
import yaml
import json

from src.logger import setup_logger

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
# from docling.datamodel.settings import settings
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

logger = setup_logger(
            "etl_app"
            # name=__name__,
            # log_dir=Path("logs"),
            # log_prefix="docling_conversion",
            # level=20,  # INFO
        )

def build_docling_converter():
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
        num_threads=8   , device=AcceleratorDevice.MPS
    )
    # Enable the profiling to measure the time spent
    # settings.debug.profile_pipeline_timings = True

    doc_converter = DocumentConverter(
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
    return doc_converter


def convert_documents(
    input_paths,
    output_dir=Path("scratch"),
    save_markdown=True,
    save_yaml=False,
    save_text=False,
    save_json=False,
):
    doc_converter = build_docling_converter()
    start_time = time.time()

    conv_results = doc_converter.convert_all(input_paths)

       # List with total time per document
    # # doc_conversion_secs = conv_results.timings["pipeline_total"].times
    # logger.info("Conversation..")
    # logger.info(f"Conversion secs: {doc_conversion_secs}")
    for res in conv_results:
        stem = res.input.file.stem
        logger.info(f"✅ Document converted: {res.input.file.name}")

        logger.debug(res.document._export_to_indented_text(max_text_len=16))    

        if save_markdown:
            md_path = output_dir / f"{stem}.md"
            md_text = res.document.export_to_markdown()
            md_path.write_text(md_text, encoding="utf-8")
            logger.info(f"   Markdown saved → {md_path}")

        if save_text:
            txt_path = output_dir / f"{stem}.txt"
            txt_text = res.document.export_to_text()
            txt_path.write_text(txt_text, encoding="utf-8")
            logger.info(f"   Text saved → {txt_path}")

        if save_yaml:
            yaml_path = output_dir / f"{stem}.yaml"
            yaml_text = yaml.safe_dump(res.document.export_to_dict())
            yaml_path.write_text(yaml_text, encoding="utf-8")
            logger.info(f"   YAML saved → {yaml_path}")

        if save_json:
            json_path = output_dir / f"{stem}.json"
            json_text = json.dumps(res.document.export_to_dict(), ensure_ascii=False, indent=2)
            json_path.write_text(json_text, encoding="utf-8")
            logger.info(f"   JSON saved → {json_path}")

    logger.info(f"Total time taken: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    input_paths = [
        Path(r"C:\path\to\your\file1.pdf"),
        Path(r"C:\path\to\your\file2.docx"),
    ]

    convert_documents(
        input_paths,
        output_dir=Path("scratch"),
        save_markdown=True,
        save_yaml=True,
        save_text=False,
        save_json=False,
    )
