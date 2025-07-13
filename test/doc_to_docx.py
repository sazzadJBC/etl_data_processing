import subprocess
import os

def convert_doc_to_docx_with_libreoffice(doc_path, output_dir):
    # Determine the LibreOffice executable path
    # This will vary based on your OS and installation
    # Common paths:
    # Windows: "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
    # Linux: "/usr/bin/libreoffice" or "/usr/lib/libreoffice/program/soffice"
    # macOS: "/Applications/LibreOffice.app/Contents/MacOS/soffice"

    libreoffice_path = "soffice" # Or the full path if not in your PATH environment variable

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    command = [
        libreoffice_path,
        "--headless",  # Run in headless mode (no GUI)
        "--convert-to", "docx",
        doc_path,
        "--outdir", output_dir
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Successfully converted '{doc_path}'. Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting '{doc_path}': {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: LibreOffice executable not found at '{libreoffice_path}'. Please ensure it's installed and in your PATH, or provide the full path.")


# Example usage:
# Make sure to replace with your actual file paths
# doc_file = "/path/to/your/document.doc"
# output_directory = "/path/to/your/output/folder"
# convert_doc_to_docx_with_libreoffice(doc_file, output_directory)