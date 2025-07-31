from agentic_doc.parse import parse

# Parse a local file
result = parse("path/to/file.pdf",result_save_dir="output_dirs")

# Get the extracted data as markdown
print("Extracted Markdown:")
print(result[0].markdown)

# Get the extracted data as structured chunks of content in a JSON schema
print("Extracted Chunks:")
print(result[0].chunks)
