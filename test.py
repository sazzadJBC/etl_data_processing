from agentic_doc.parse import parse
from dotenv import load_dotenv
load_dotenv(override=True)
# Parse a local file
result = parse("/Users/jbc/Documents/SevenSix/etl_data_processing/sevensix_data/機密レベル1/技術本部/frush/広報（youtube動画）/中村youtube/frush応用編①/frush応用①_指示書・テキスト・図/frush応用①_指示書.pdf",result_save_dir="output_dirs")

# Get the extracted data as markdown
print("Extracted Markdown:")
print(result[0].markdown)

# Get the extracted data as structured chunks of content in a JSON schema
print("Extracted Chunks:")
print(result[0].chunks)