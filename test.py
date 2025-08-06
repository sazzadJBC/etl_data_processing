from agentic_doc.parse import parse
from dotenv import load_dotenv
load_dotenv(override=True)
# Parse a local file
result = parse("/Users/jbc/Documents/SevenSix/etl_data_processing/test_data/981055885_日本レーザ_ｃｃｒ全文ｐｄｆｂ_20240409.pdf",result_save_dir="output_dirs1")

# Get the extracted data as markdown
print("Extracted Markdown:")
print(result[0].markdown)

# Get the extracted data as structured chunks of content in a JSON schema
print("Extracted Chunks:")
print(result[0].chunks)