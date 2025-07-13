import re
import logging
from pathlib import Path
from src.logger import setup_logger
# -----------------------
# Configure logger
# -----------------------
logger = setup_logger("etl_app")



def txt_to_md(input_path, output_path):
    """
    Convert a .txt file to Markdown, detecting:
    - headings
    - lists
    - code blocks
    - paragraphs
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    logger.info(f"Starting conversion: {input_path} → {output_path}")

    with input_path.open(encoding='utf-8') as infile, \
         output_path.open('w', encoding='utf-8') as outfile:

        paragraph = []
        in_code_block = False

        for line in infile:
            raw_line = line
            line = line.rstrip('\n')

            # Detect start/end of indented code block
            if is_indented(line):
                if not in_code_block:
                    # Write any current paragraph first
                    if paragraph:
                        outfile.write('\n'.join(paragraph) + '\n\n')
                        paragraph = []
                    outfile.write("```\n")
                    in_code_block = True

                outfile.write(raw_line)  # preserve original line including leading spaces
                continue
            else:
                if in_code_block:
                    outfile.write("```\n\n")
                    in_code_block = False

            # Skip empty lines
            if not line.strip():
                if paragraph:
                    outfile.write('\n'.join(paragraph) + '\n\n')
                    paragraph = []
                continue

            # Detect headings
            if is_heading(line):
                if paragraph:
                    outfile.write('\n'.join(paragraph) + '\n\n')
                    paragraph = []
                outfile.write(f"# {line.strip().title()}\n\n")
                continue

            # Detect lists
            if is_list_item(line):
                paragraph.append(line+"\n")
                continue

            # Normal text
            paragraph.append(line)

        # Finalize file
        if in_code_block:
            outfile.write("```\n\n")
            in_code_block = False

        if paragraph:
            outfile.write('\n'.join(paragraph) + '\n')

    logger.info(f"Conversion complete: {output_path}")


def is_heading(line):
    line = line.strip()
    if line.isupper():
        return True
    if re.match(r'^(=|-){3,}$', line):
        return True
    return False


def is_list_item(line):
    return bool(re.match(r'^(\s*)(-|\*)\s+', line))


def is_indented(line):
    return bool(re.match(r'^( {4}|\t)', line))


def text_to_md(input_txt, output_md):
    """    Convert a text file to Markdown format."""
    txt_to_md(input_txt, output_md)


if __name__ == "__main__":
        # Example hard-coded paths
    input_txt = Path("example.txt")
    output_md = Path("example.md")
    text_to_md(input_txt, output_md)
