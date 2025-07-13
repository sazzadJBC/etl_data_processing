from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

import time
from pathlib import Path

from docling_core.types.doc import PictureItem
pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2
pipeline_options.do_picture_classification = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})


start_time = time.time()
# result = converter.convert("https://arxiv.org/pdf/2501.17887")
result = converter.convert(Path("data/s3_downloads/営業本部/メーカー別/finisar/07. 代理店会議資料/2020年 定例会/finisar stagger chart_sevensix_20200311.xlsx"))
end_time = time.time() - start_time

print(f"Document converted in {end_time:.2f} seconds.")

doc_filename = result.input.file.stem

for element, _level in result.document.iterate_items():
        if isinstance(element, PictureItem):
              print(element)


# Export Markdown format:
with Path(f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
    fp.write(result.document.export_to_markdown())


from docling_core.types.doc.document import PictureDescriptionData
from IPython import display
doc = result.document
html_buffer = []
# display the first 5 pictures and their captions and annotations:
for pic in doc.pictures[:5]:
    html_item = (
        f"Picture {pic.self_ref}"
        f''
        f"Caption{pic.caption_text(doc=doc)}"
    )
    for annotation in pic.annotations:
        if not isinstance(annotation, PictureDescriptionData):
            html_item += (
            f"Annotations \n"
        )
            continue
        html_item += (
            f"Annotations ({annotation.provenance}){annotation.text}\n"
        )
    html_buffer.append(html_item)
display.HTML("".join(html_buffer))